using System.Text;
using System.Text.RegularExpressions;
using Oracle.ManagedDataAccess.Client;

Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

if (args.Length < 2)
{
    Console.Error.WriteLine("Usage: OracleApply <connection-env-var> <script.sql> [--stop-on-error] [--encoding=utf8|cp1251]");
    return 2;
}

var connectionString = Environment.GetEnvironmentVariable(args[0]);
if (string.IsNullOrWhiteSpace(connectionString))
{
    Console.Error.WriteLine($"Environment variable {args[0]} is not set.");
    return 2;
}

if (args[1].Equals("--query", StringComparison.OrdinalIgnoreCase))
{
    if (args.Length < 3)
    {
        Console.Error.WriteLine("Usage: OracleApply <connection-env-var> --query <select-sql>");
        return 2;
    }

    await using var queryConnection = new OracleConnection(connectionString);
    await queryConnection.OpenAsync();
    await using var command = queryConnection.CreateCommand();
    command.CommandText = args[2];
    command.CommandTimeout = 0;
    await using var reader = await command.ExecuteReaderAsync();

    for (var i = 0; i < reader.FieldCount; i++)
    {
        if (i > 0)
        {
            Console.Write('\t');
        }
        Console.Write(reader.GetName(i));
    }
    Console.WriteLine();

    while (await reader.ReadAsync())
    {
        for (var i = 0; i < reader.FieldCount; i++)
        {
            if (i > 0)
            {
                Console.Write('\t');
            }

            Console.Write(reader.IsDBNull(i) ? "" : reader.GetValue(i).ToString());
        }
        Console.WriteLine();
    }

    return 0;
}

if (args[1].Equals("--export-rabaev", StringComparison.OrdinalIgnoreCase))
{
    if (args.Length < 3)
    {
        Console.Error.WriteLine("Usage: OracleApply <connection-env-var> --export-rabaev <out-dir>");
        return 2;
    }

    await using var exportConnection = new OracleConnection(connectionString);
    await exportConnection.OpenAsync();
    await RabaevSqlExporter.ExportAsync(exportConnection, Path.GetFullPath(args[2]));
    return 0;
}

var scriptPath = Path.GetFullPath(args[1]);
var stopOnError = args.Contains("--stop-on-error", StringComparer.OrdinalIgnoreCase);
var scriptEncoding = GetScriptEncoding(args);

await using var connection = new OracleConnection(connectionString);
await connection.OpenAsync();

var runner = new SqlPlusLikeRunner(connection, stopOnError, scriptEncoding);
await runner.RunFileAsync(scriptPath);

Console.WriteLine($"Done. Statements={runner.StatementCount}; Errors={runner.ErrorCount}");
return runner.ErrorCount == 0 ? 0 : 1;

static Encoding GetScriptEncoding(string[] args)
{
    var encodingArg = args.FirstOrDefault(arg => arg.StartsWith("--encoding=", StringComparison.OrdinalIgnoreCase));
    var encodingName = encodingArg?.Split('=', 2)[1].Trim().ToLowerInvariant();
    return encodingName switch
    {
        null or "" or "utf8" or "utf-8" => new UTF8Encoding(false, true),
        "cp1251" or "windows-1251" or "1251" => Encoding.GetEncoding(1251),
        _ => throw new ArgumentException($"Unsupported script encoding: {encodingName}")
    };
}

internal sealed class SqlPlusLikeRunner
{
    private static readonly Regex PlSqlStart = new(
        @"^\s*(create\s+(or\s+replace\s+)?(editionable\s+|noneditionable\s+)?(function|procedure|package|trigger|type)|declare|begin)\b",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);

    private readonly OracleConnection connection;
    private readonly Encoding scriptEncoding;
    private readonly HashSet<string> includeStack = new(StringComparer.OrdinalIgnoreCase);
    private bool stopOnError;

    public SqlPlusLikeRunner(OracleConnection connection, bool stopOnError, Encoding scriptEncoding)
    {
        this.connection = connection;
        this.stopOnError = stopOnError;
        this.scriptEncoding = scriptEncoding;
    }

    public int StatementCount { get; private set; }
    public int ErrorCount { get; private set; }

    public async Task RunFileAsync(string path)
    {
        path = Path.GetFullPath(path);
        if (!File.Exists(path))
        {
            throw new FileNotFoundException("SQL script not found.", path);
        }

        if (!includeStack.Add(path))
        {
            throw new InvalidOperationException($"Recursive include detected: {path}");
        }

        Console.WriteLine($"-- running {path}");

        var current = new StringBuilder();
        var currentStartLine = 0;
        var inPlSql = false;
        var lines = await File.ReadAllLinesAsync(path, scriptEncoding);

        for (var i = 0; i < lines.Length; i++)
        {
            var lineNo = i + 1;
            var line = lines[i];
            var trimmed = line.Trim();

            if (current.Length == 0)
            {
                if (trimmed.Length == 0 || trimmed.StartsWith("--"))
                {
                    continue;
                }

                if (trimmed.StartsWith("prompt ", StringComparison.OrdinalIgnoreCase))
                {
                    Console.WriteLine(trimmed[7..]);
                    continue;
                }

                if (trimmed.Equals("show errors", StringComparison.OrdinalIgnoreCase)
                    || trimmed.StartsWith("set ", StringComparison.OrdinalIgnoreCase)
                    || trimmed.StartsWith("spool ", StringComparison.OrdinalIgnoreCase)
                    || trimmed.StartsWith("exit", StringComparison.OrdinalIgnoreCase)
                    || trimmed.StartsWith("rem ", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                if (trimmed.StartsWith("whenever sqlerror exit", StringComparison.OrdinalIgnoreCase))
                {
                    stopOnError = true;
                    continue;
                }

                if (trimmed.StartsWith("whenever ", StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                if (trimmed.StartsWith("@"))
                {
                    var include = trimmed.TrimStart('@').Trim();
                    var includePath = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(path)!, include));
                    await RunFileAsync(includePath);
                    continue;
                }

                if (trimmed == "/")
                {
                    continue;
                }

                currentStartLine = lineNo;
                inPlSql = PlSqlStart.IsMatch(trimmed);
            }

            if (inPlSql && trimmed == "/")
            {
                await ExecuteAsync(current.ToString(), path, currentStartLine);
                current.Clear();
                currentStartLine = 0;
                inPlSql = false;
                continue;
            }

            current.AppendLine(line);

            if (!inPlSql && trimmed.EndsWith(';'))
            {
                var sql = current.ToString().TrimEnd();
                sql = sql[..^1];
                await ExecuteAsync(sql, path, currentStartLine);
                current.Clear();
                currentStartLine = 0;
            }
        }

        if (current.Length > 0)
        {
            await ExecuteAsync(current.ToString(), path, currentStartLine);
        }

        includeStack.Remove(path);
    }

    private async Task ExecuteAsync(string sql, string path, int lineNo)
    {
        if (string.IsNullOrWhiteSpace(sql))
        {
            return;
        }

        StatementCount++;
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        command.CommandTimeout = 0;

        try
        {
            await command.ExecuteNonQueryAsync();
        }
        catch (OracleException ex)
        {
            ErrorCount++;
            var firstLine = sql.Trim().Split('\n', '\r').FirstOrDefault(s => !string.IsNullOrWhiteSpace(s))?.Trim();
            Console.Error.WriteLine($"ERROR {Path.GetFileName(path)}:{lineNo}: ORA-{ex.Number}: {ex.Message}");
            Console.Error.WriteLine($"SQL: {firstLine}");

            if (stopOnError)
            {
                throw;
            }
        }
    }
}

internal static class RabaevSqlExporter
{
    private const string Owner = "RABAEV";
    private const long MaxDataFileBytes = 45L * 1024L * 1024L;

    public static async Task ExportAsync(OracleConnection connection, string outDir)
    {
        Directory.CreateDirectory(outDir);
        var ddlDir = Path.Combine(outDir, "ddl");
        var dataDir = Path.Combine(outDir, "data");
        var metaDir = Path.Combine(outDir, "metadata");
        Directory.CreateDirectory(ddlDir);
        Directory.CreateDirectory(dataDir);
        Directory.CreateDirectory(metaDir);

        await ExecuteNonQueryAsync(connection, """
            begin
              dbms_metadata.set_transform_param(dbms_metadata.session_transform, 'SQLTERMINATOR', true);
              dbms_metadata.set_transform_param(dbms_metadata.session_transform, 'PRETTY', true);
              dbms_metadata.set_transform_param(dbms_metadata.session_transform, 'SEGMENT_ATTRIBUTES', false);
              dbms_metadata.set_transform_param(dbms_metadata.session_transform, 'STORAGE', false);
              dbms_metadata.set_transform_param(dbms_metadata.session_transform, 'TABLESPACE', false);
            end;
            """);

        var tables = await LoadNamesAsync(connection, """
            select table_name
              from dba_tables
             where owner = 'RABAEV'
               and table_name not like 'BIN$%'
               and nested = 'NO'
             order by table_name
            """);

        var sequences = await LoadNamesAsync(connection, """
            select sequence_name
              from dba_sequences
             where sequence_owner = 'RABAEV'
             order by sequence_name
            """);

        var objectTypes = new (string TypeName, string FileName)[]
        {
            ("TABLE", "001_tables.sql"),
            ("SEQUENCE", "002_sequences.sql"),
            ("VIEW", "003_views.sql"),
            ("PACKAGE", "004_packages.sql"),
            ("PACKAGE_BODY", "005_package_bodies.sql"),
            ("FUNCTION", "006_functions.sql"),
            ("PROCEDURE", "007_procedures.sql"),
            ("TRIGGER", "008_triggers.sql"),
            ("INDEX", "009_indexes.sql")
        };

        var restoreFiles = new List<string>();

        foreach (var (typeName, fileName) in objectTypes)
        {
            var filePath = Path.Combine(ddlDir, fileName);
            var count = await WriteDdlFileAsync(connection, typeName, filePath);
            if (count > 0)
            {
                restoreFiles.Add($"@ddl/{fileName}");
            }
        }

        var dataFiles = new List<string>();
        foreach (var table in tables)
        {
            dataFiles.AddRange(await ExportTableDataAsync(connection, dataDir, table));
        }

        await WriteRestoreScriptAsync(outDir, restoreFiles, dataFiles);
        await WriteVerifyScriptAsync(outDir);
        await WriteMetadataAsync(connection, metaDir, tables, sequences);

        Console.WriteLine($"Exported {tables.Count} tables, {sequences.Count} sequences.");
        Console.WriteLine($"Output: {outDir}");
    }

    private static async Task<int> WriteDdlFileAsync(OracleConnection connection, string typeName, string filePath)
    {
        var names = await LoadNamesAsync(connection, ObjectNameSql(typeName));
        await using var writer = new StreamWriter(filePath, false, new UTF8Encoding(false));
        await writer.WriteLineAsync("set define off");
        await writer.WriteLineAsync("set sqlblanklines on");
        await writer.WriteLineAsync();

        var count = 0;
        foreach (var name in names)
        {
            var ddl = await GetDdlAsync(connection, typeName, name);
            if (string.IsNullOrWhiteSpace(ddl))
            {
                continue;
            }

            await writer.WriteLineAsync($"prompt {typeName} {name}");
            await writer.WriteLineAsync(ddl.TrimEnd());
            await writer.WriteLineAsync();
            count++;
        }

        return count;
    }

    private static string ObjectNameSql(string typeName)
    {
        var objectType = typeName == "PACKAGE_BODY" ? "PACKAGE BODY" : typeName;
        return $"""
            select object_name
              from dba_objects
             where owner = 'RABAEV'
               and object_type = '{objectType}'
               and object_name not like 'BIN$%'
             order by object_name
            """;
    }

    private static async Task<string?> GetDdlAsync(OracleConnection connection, string typeName, string objectName)
    {
        await using var command = connection.CreateCommand();
        command.BindByName = true;
        command.CommandText = "select dbms_metadata.get_ddl(:object_type, :object_name, :owner) from dual";
        command.Parameters.Add("object_type", OracleDbType.Varchar2).Value = typeName;
        command.Parameters.Add("object_name", OracleDbType.Varchar2).Value = objectName;
        command.Parameters.Add("owner", OracleDbType.Varchar2).Value = Owner;

        await using var reader = await command.ExecuteReaderAsync();
        if (!await reader.ReadAsync() || reader.IsDBNull(0))
        {
            return null;
        }

        return reader.GetValue(0).ToString();
    }

    private static async Task<List<string>> ExportTableDataAsync(OracleConnection connection, string dataDir, string table)
    {
        var columns = await LoadColumnsAsync(connection, table);
        var files = new List<string>();
        var part = 1;
        var rowCount = 0;
        var fileRowCount = 0;
        var currentFile = OpenDataWriter(dataDir, table, part, files);

        try
        {
            var columnList = string.Join(", ", columns.Select(c => QuoteIdent(c.Name)));
            var sql = $"select {columnList} from {QuoteIdent(Owner)}.{QuoteIdent(table)}";
            await using var command = connection.CreateCommand();
            command.CommandText = sql;
            command.FetchSize = 1024 * 1024;
            command.CommandTimeout = 0;
            await using var reader = await command.ExecuteReaderAsync();

            while (await reader.ReadAsync())
            {
                if (currentFile.BaseStream.Length > MaxDataFileBytes && fileRowCount > 0)
                {
                    await currentFile.WriteLineAsync("commit;");
                    await currentFile.DisposeAsync();
                    part++;
                    fileRowCount = 0;
                    currentFile = OpenDataWriter(dataDir, table, part, files);
                }

                var values = new string[columns.Count];
                for (var i = 0; i < columns.Count; i++)
                {
                    values[i] = SqlLiteral(reader, i, columns[i].DataType);
                }

                await currentFile.WriteLineAsync($"insert into {QuoteIdent(Owner)}.{QuoteIdent(table)} ({columnList}) values ({string.Join(", ", values)});");
                rowCount++;
                fileRowCount++;

                if (fileRowCount % 1000 == 0)
                {
                    await currentFile.WriteLineAsync("commit;");
                }
            }

            await currentFile.WriteLineAsync("commit;");
        }
        finally
        {
            await currentFile.DisposeAsync();
        }

        Console.WriteLine($"Data {table}: {rowCount} rows into {files.Count} file(s)");
        return files.Select(f => $"@data/{Path.GetFileName(f)}").ToList();
    }

    private static StreamWriter OpenDataWriter(string dataDir, string table, int part, List<string> files)
    {
        var file = Path.Combine(dataDir, $"{table.ToLowerInvariant()}_{part:000}.sql");
        files.Add(file);
        var writer = new StreamWriter(file, false, new UTF8Encoding(false));
        writer.WriteLine("set define off");
        writer.WriteLine($"prompt Loading {table} part {part:000}");
        return writer;
    }

    private static async Task<List<ColumnInfo>> LoadColumnsAsync(OracleConnection connection, string table)
    {
        await using var command = connection.CreateCommand();
        command.BindByName = true;
        command.CommandText = """
            select column_name, data_type
              from dba_tab_columns
             where owner = 'RABAEV'
               and table_name = :table_name
             order by column_id
            """;
        command.Parameters.Add("table_name", OracleDbType.Varchar2).Value = table;

        var columns = new List<ColumnInfo>();
        await using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            columns.Add(new ColumnInfo(reader.GetString(0), reader.GetString(1)));
        }

        return columns;
    }

    private static string SqlLiteral(OracleDataReader reader, int ordinal, string dataType)
    {
        if (reader.IsDBNull(ordinal))
        {
            return "null";
        }

        dataType = dataType.ToUpperInvariant();
        if (dataType.Contains("CHAR") || dataType is "CLOB" or "NCLOB")
        {
            return StringLiteral(reader.GetValue(ordinal).ToString() ?? "");
        }

        if (dataType == "DATE")
        {
            var value = reader.GetDateTime(ordinal);
            return $"to_date('{value:yyyy-MM-dd HH:mm:ss}', 'YYYY-MM-DD HH24:MI:SS')";
        }

        if (dataType.StartsWith("TIMESTAMP", StringComparison.OrdinalIgnoreCase))
        {
            var value = reader.GetDateTime(ordinal);
            return $"to_timestamp('{value:yyyy-MM-dd HH:mm:ss.ffffff}', 'YYYY-MM-DD HH24:MI:SS.FF')";
        }

        if (dataType == "NUMBER" || dataType is "FLOAT" or "BINARY_FLOAT" or "BINARY_DOUBLE")
        {
            return reader.GetOracleValue(ordinal).ToString()?.Replace(',', '.') ?? "null";
        }

        if (dataType == "RAW")
        {
            return $"hextoraw('{BitConverter.ToString((byte[])reader.GetValue(ordinal)).Replace("-", "")}')";
        }

        return StringLiteral(reader.GetValue(ordinal).ToString() ?? "");
    }

    private static string StringLiteral(string value)
    {
        if (value.Length <= 3900)
        {
            return $"'{value.Replace("'", "''")}'";
        }

        var chunks = new List<string>();
        for (var i = 0; i < value.Length; i += 3900)
        {
            var chunk = value.Substring(i, Math.Min(3900, value.Length - i));
            chunks.Add($"to_clob('{chunk.Replace("'", "''")}')");
        }

        return string.Join(" || ", chunks);
    }

    private static async Task WriteRestoreScriptAsync(string outDir, IReadOnlyList<string> ddlFiles, IReadOnlyList<string> dataFiles)
    {
        await using var writer = new StreamWriter(Path.Combine(outDir, "restore.sql"), false, new UTF8Encoding(false));
        await writer.WriteLineAsync("set define off");
        await writer.WriteLineAsync("set sqlblanklines on");
        await writer.WriteLineAsync("whenever sqlerror exit failure rollback");
        await writer.WriteLineAsync();
        await writer.WriteLineAsync("prompt Restore RABAEV schema snapshot");
        await writer.WriteLineAsync("prompt Run as SYSTEM or another privileged user connected to the target PDB.");
        await writer.WriteLineAsync();
        foreach (var file in ddlFiles)
        {
            await writer.WriteLineAsync(file);
        }
        await writer.WriteLineAsync();
        foreach (var file in dataFiles)
        {
            await writer.WriteLineAsync(file);
        }
        await writer.WriteLineAsync();
        await writer.WriteLineAsync("@verify.sql");
    }

    private static async Task WriteVerifyScriptAsync(string outDir)
    {
        await File.WriteAllTextAsync(Path.Combine(outDir, "verify.sql"), """
            set define off
            select object_type, status, count(*) cnt
              from dba_objects
             where owner = 'RABAEV'
             group by object_type, status
             order by object_type, status;

            select 'RRL_ARTICULS' table_name, count(*) cnt from RABAEV.RRL_ARTICULS
            union all select 'RRL_CELLS', count(*) from RABAEV.RRL_CELLS
            union all select 'RUSERS', count(*) from RABAEV.RUSERS
            union all select 'RRL_TRANSPORT_TASK', count(*) from RABAEV.RRL_TRANSPORT_TASK
            union all select 'RRL_SBORKA_PALLETS', count(*) from RABAEV.RRL_SBORKA_PALLETS
            union all select 'RRL_SBORKA_PALLET_ROWS', count(*) from RABAEV.RRL_SBORKA_PALLET_ROWS;
            """, new UTF8Encoding(false));
    }

    private static async Task WriteMetadataAsync(OracleConnection connection, string metaDir, IReadOnlyList<string> tables, IReadOnlyList<string> sequences)
    {
        await WriteQueryAsync(connection, Path.Combine(metaDir, "object_status.tsv"), """
            select object_type, status, count(*) cnt
              from dba_objects
             where owner = 'RABAEV'
             group by object_type, status
             order by object_type, status
            """);

        await WriteQueryAsync(connection, Path.Combine(metaDir, "table_counts.tsv"), """
            select table_name, num_rows
              from dba_tables
             where owner = 'RABAEV'
             order by table_name
            """);

        await File.WriteAllLinesAsync(Path.Combine(metaDir, "tables.txt"), tables, new UTF8Encoding(false));
        await File.WriteAllLinesAsync(Path.Combine(metaDir, "sequences.txt"), sequences, new UTF8Encoding(false));
    }

    private static async Task WriteQueryAsync(OracleConnection connection, string path, string sql)
    {
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        await using var reader = await command.ExecuteReaderAsync();
        await using var writer = new StreamWriter(path, false, new UTF8Encoding(false));

        for (var i = 0; i < reader.FieldCount; i++)
        {
            if (i > 0)
            {
                await writer.WriteAsync('\t');
            }
            await writer.WriteAsync(reader.GetName(i));
        }
        await writer.WriteLineAsync();

        while (await reader.ReadAsync())
        {
            for (var i = 0; i < reader.FieldCount; i++)
            {
                if (i > 0)
                {
                    await writer.WriteAsync('\t');
                }
                await writer.WriteAsync(reader.IsDBNull(i) ? "" : reader.GetValue(i).ToString());
            }
            await writer.WriteLineAsync();
        }
    }

    private static async Task<List<string>> LoadNamesAsync(OracleConnection connection, string sql)
    {
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        await using var reader = await command.ExecuteReaderAsync();
        var values = new List<string>();
        while (await reader.ReadAsync())
        {
            values.Add(reader.GetString(0));
        }
        return values;
    }

    private static async Task ExecuteNonQueryAsync(OracleConnection connection, string sql)
    {
        await using var command = connection.CreateCommand();
        command.CommandText = sql;
        await command.ExecuteNonQueryAsync();
    }

    private static string QuoteIdent(string ident) => "\"" + ident.Replace("\"", "\"\"") + "\"";

    private sealed record ColumnInfo(string Name, string DataType);
}
