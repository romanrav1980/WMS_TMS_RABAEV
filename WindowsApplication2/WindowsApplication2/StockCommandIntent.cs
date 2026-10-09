using System;
using System.Data;
using System.Data.OracleClient;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Xml;

namespace WindowsApplication2
{
    // An intent is persisted before Oracle is called. Failed/uncertain calls retain it.
    internal sealed class StockCommandIntent
    {
        private readonly string path;
        internal readonly string OperationId;
        private StockCommandIntent(string file, string operation)
        {
            path = file;
            OperationId = operation;
        }

        private static string DirectoryPath()
        {
            string folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "NICORA");
            folder = Path.Combine(folder, "stock-command-intents");
            Directory.CreateDirectory(folder);
            return folder;
        }

        private static string Digest(string text)
        {
            using (SHA256 hash = SHA256.Create())
            {
                byte[] bytes = hash.ComputeHash(Encoding.UTF8.GetBytes(text));
                StringBuilder result = new StringBuilder();
                foreach (byte value in bytes) result.Append(value.ToString("x2", CultureInfo.InvariantCulture));
                return result.ToString();
            }
        }

        private static void Part(StringBuilder output, string value)
        {
            value = value ?? "";
            output.Append(value.Length.ToString(CultureInfo.InvariantCulture)).Append(":").Append(value);
        }

        private static string ValueText(object value)
        {
            if (value == null || value == DBNull.Value) return "";
            if (value is DateTime) return ((DateTime)value).ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
            IFormattable formatted = value as IFormattable;
            return formatted == null ? value.ToString() : formatted.ToString(null, CultureInfo.InvariantCulture);
        }

        internal static StockCommandIntent Prepare(OracleCommand command, string actor, string sourceIdentity)
        {
            StringBuilder slot = new StringBuilder();
            Part(slot, command.Connection.DataSource);
            Part(slot, command.CommandText);
            Part(slot, actor);
            Part(slot, sourceIdentity);
            StringBuilder body = new StringBuilder();
            foreach (OracleParameter parameter in command.Parameters)
            {
                if (parameter.Direction != ParameterDirection.Input || parameter.ParameterName == "p_operation_id") continue;
                Part(body, parameter.ParameterName);
                Part(body, ValueText(parameter.Value));
            }
            string signature = Digest(body.ToString());
            string file = Path.Combine(DirectoryPath(), Digest(slot.ToString()) + ".xml");
            if (!File.Exists(file))
            {
                XmlDocument document = new XmlDocument();
                XmlElement root = document.CreateElement("stockIntent");
                root.SetAttribute("operation", "DESKTOP.STOCK:" + Guid.NewGuid().ToString("N"));
                root.SetAttribute("signature", signature);
                root.SetAttribute("command", command.CommandText);
                root.SetAttribute("actor", actor ?? "");
                foreach (OracleParameter parameter in command.Parameters)
                {
                    if (parameter.Direction != ParameterDirection.Input || parameter.ParameterName == "p_operation_id") continue;
                    XmlElement input = document.CreateElement("parameter");
                    input.SetAttribute("name", parameter.ParameterName);
                    input.SetAttribute("type", parameter.OracleType.ToString());
                    input.SetAttribute("null", (parameter.Value == null || parameter.Value == DBNull.Value) ? "true" : "false");
                    input.InnerText = ValueText(parameter.Value);
                    root.AppendChild(input);
                }
                document.AppendChild(root);
                string temp = file + "." + Guid.NewGuid().ToString("N") + ".tmp";
                try
                {
                    using (FileStream stream = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
                    {
                        document.Save(stream);
                        stream.Flush();
                    }
                    try { File.Move(temp, file); }
                    catch (IOException) { if (!File.Exists(file)) throw; }
                }
                finally { if (File.Exists(temp)) File.Delete(temp); }
            }
            XmlDocument saved = new XmlDocument();
            saved.Load(file);
            XmlElement entry = saved.DocumentElement;
            if (entry == null || entry.GetAttribute("signature") != signature)
                throw new InvalidOperationException("An unresolved stock command exists for this source. Repeat its original parameters before changing them. Saved parameters: " + file);
            string operation = entry.GetAttribute("operation");
            if (operation.Length == 0)
                throw new InvalidOperationException("Stored stock command has no operation ID.");
            command.Parameters.Add("p_operation_id", OracleType.VarChar).Value = operation;
            return new StockCommandIntent(file, operation);
        }

        internal void Confirm()
        {
            // Deleting only the confirmed intent permits a new action on the same source.
            // Oracle success is authoritative. Local cleanup failure must not be reported
            // as failed posting; retaining the intent still makes its retry idempotent.
            try { if (File.Exists(path)) File.Delete(path); }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }

        internal static int InventoryRevision(string database, string actor, int warehouse, string fileHash, RevisionFactory create)
        {
            StringBuilder identity = new StringBuilder();
            Part(identity, database); Part(identity, actor); Part(identity, warehouse.ToString(CultureInfo.InvariantCulture)); Part(identity, fileHash);
            string path = Path.Combine(DirectoryPath(), "inventory-" + Digest(identity.ToString()) + ".xml");
            if (File.Exists(path))
            {
                XmlDocument existing = new XmlDocument(); existing.Load(path);
                return Int32.Parse(existing.DocumentElement.GetAttribute("revision"), CultureInfo.InvariantCulture);
            }
            int revision = create();
            if (revision < 1) throw new InvalidOperationException("Inventory revision was not created.");
            XmlDocument document = new XmlDocument(); XmlElement root = document.CreateElement("inventoryDocument");
            root.SetAttribute("revision", revision.ToString(CultureInfo.InvariantCulture)); document.AppendChild(root);
            string temp = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
            try
            {
                using (FileStream stream = new FileStream(temp, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough)) { document.Save(stream); stream.Flush(); }
                try { File.Move(temp, path); } catch (IOException) { if (!File.Exists(path)) throw; }
            }
            finally { if (File.Exists(temp)) File.Delete(temp); }
            XmlDocument saved = new XmlDocument(); saved.Load(path);
            return Int32.Parse(saved.DocumentElement.GetAttribute("revision"), CultureInfo.InvariantCulture);
        }

        internal static string FileDigest(string path)
        {
            using (SHA256 hash = SHA256.Create())
            using (FileStream stream = File.OpenRead(path))
            {
                byte[] bytes = hash.ComputeHash(stream); StringBuilder result = new StringBuilder();
                foreach (byte value in bytes) result.Append(value.ToString("x2", CultureInfo.InvariantCulture));
                return result.ToString();
            }
        }

        internal delegate int RevisionFactory();
    }
}
