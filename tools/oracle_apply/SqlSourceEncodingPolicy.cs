using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

internal sealed class SqlSourceEncodingPolicy
{
    private readonly Dictionary<string, (Encoding Encoding, string Sha256)> entries = new(StringComparer.OrdinalIgnoreCase);
    public SqlSourceEncodingPolicy(string? manifestPath)
    {
        if (manifestPath is null) return;
        manifestPath = Path.GetFullPath(manifestPath);
        using var document = JsonDocument.Parse(File.ReadAllText(manifestPath, Encoding.UTF8));
        var root = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(manifestPath)!, document.RootElement.GetProperty("sourceRoot").GetString()!));
        foreach (var item in document.RootElement.GetProperty("files").EnumerateObject())
        {
            var file = Path.GetFullPath(Path.Combine(root, item.Name));
            if (!file.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Encoding manifest path escapes its source root");
            var encoding = item.Value.GetProperty("encoding").GetString() switch
            {
                "cp1251" => Encoding.GetEncoding(1251, EncoderFallback.ExceptionFallback, DecoderFallback.ExceptionFallback),
                "utf8" => new UTF8Encoding(false, true),
                _ => throw new ArgumentException("Unsupported manifest encoding")
            };
            entries.Add(file, (encoding, item.Value.GetProperty("sha256").GetString()!));
        }
    }
    public Encoding Resolve(string path, Encoding fallback)
    {
        if (!entries.TryGetValue(Path.GetFullPath(path), out var entry)) return fallback;
        var actual = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
        if (!actual.Equals(entry.Sha256, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException($"Source encoding manifest hash mismatch: {path}");
        Console.WriteLine($"SOURCE_ENCODING {Path.GetFileName(path)}: {entry.Encoding.WebName} (verified SHA256)");
        return entry.Encoding;
    }
}
