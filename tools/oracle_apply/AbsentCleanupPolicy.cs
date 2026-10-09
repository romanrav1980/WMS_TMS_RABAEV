using System.Text.RegularExpressions;

internal static class AbsentCleanupPolicy
{
    // Exported legacy scripts start with cleanup before CREATE. Only absence of
    // the exact RABAEV object/primary key is optional; DML/privilege errors are not.
    private const string Name = @"(?:RABAEV\.)(?:[A-Z][A-Z0-9_$#]*|""[A-Z][A-Z0-9_$#]*"")";
    public static bool Allows(string sql, int errorNumber)
    {
        var drop = Regex.Match(sql.Trim(), @"^DROP\s+(TABLE|VIEW|SEQUENCE|INDEX|TRIGGER|SYNONYM|FUNCTION|PROCEDURE|PACKAGE(?:\s+BODY)?)\s+" + Name + @"(?:\s+CASCADE\s+CONSTRAINTS)?(?:\s+PURGE)?\s*$", RegexOptions.IgnoreCase);
        if (drop.Success)
        {
            var kind = Regex.Replace(drop.Groups[1].Value.ToUpperInvariant(), @"\s+", " ");
            var expected = kind switch
            {
                "TABLE" or "VIEW" => 942,
                "SEQUENCE" => 2289,
                "INDEX" => 1418,
                "TRIGGER" => 4080,
                "SYNONYM" => 1434,
                "FUNCTION" or "PROCEDURE" or "PACKAGE" or "PACKAGE BODY" => 4043,
                _ => -1
            };
            return errorNumber == expected;
        }
        return (errorNumber is 942 or 2441) && Regex.IsMatch(sql.Trim(),
            @"^ALTER\s+TABLE\s+" + Name + @"\s+DROP\s+PRIMARY\s+KEY(?:\s+CASCADE)?\s*$", RegexOptions.IgnoreCase);
    }
}
