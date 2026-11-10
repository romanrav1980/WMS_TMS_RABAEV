using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Windows.Forms;
class Setup {
 static readonly string LogPath=Path.Combine(Path.GetTempPath(),"SNS-Setup.log");
 static void Log(string text){File.AppendAllText(LogPath,DateTime.Now.ToString("s")+" "+text+Environment.NewLine);}
 [STAThread] static int Main(string[] args){
  bool quiet=Array.IndexOf(args,"/quiet")>=0; string dest=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"SNS Delivery Schedule");
  for(int i=0;i<args.Length-1;i++)if(args[i]=="/dir")dest=Path.GetFullPath(args[i+1]);
  try{
   Log("START "+dest);
   if(!Environment.Is64BitOperatingSystem)throw new Exception("Требуется 64-разрядная Windows 10 или Windows 11.");
   if(!quiet&&MessageBox.Show("Установить график поставок?\n\nПапка: "+dest,"Установка",MessageBoxButtons.OKCancel,MessageBoxIcon.Question)!=DialogResult.OK)return 0;
   Directory.CreateDirectory(dest);
   string bundledPython=Path.Combine(dest,"python","pythonw.exe");
   foreach(var process in Process.GetProcessesByName("pythonw")) {
    try { if(String.Equals(process.MainModule.FileName,bundledPython,StringComparison.OrdinalIgnoreCase)){process.Kill();process.WaitForExit(10000);} }
    catch(System.ComponentModel.Win32Exception) { }
    finally { process.Dispose(); }
   }
   string database=Path.Combine(dest,"runtime","schedule.sqlite3");
   if(File.Exists(database)){
    string backups=Path.Combine(dest,"runtime","backups");Directory.CreateDirectory(backups);
    File.Copy(database,Path.Combine(backups,"before-install-"+DateTime.Now.ToString("yyyyMMdd-HHmmss-fffffff")+".sqlite3"));
   }
   using(var stream=Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip"))using(var zip=new ZipArchive(stream,ZipArchiveMode.Read))foreach(var entry in zip.Entries){
    if(String.IsNullOrEmpty(entry.Name))continue;string path=Path.GetFullPath(Path.Combine(dest,entry.FullName.Replace('/',Path.DirectorySeparatorChar)));
    if(!path.StartsWith(Path.GetFullPath(dest).TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new Exception("Неверный путь в установщике");
    Directory.CreateDirectory(Path.GetDirectoryName(path));if(entry.FullName.Equals("runtime/schedule.sqlite3",StringComparison.OrdinalIgnoreCase)&&File.Exists(path))continue;entry.ExtractToFile(path,true);
   }
   Log("Files extracted. Checking Python, application and database.");
   var check=new ProcessStartInfo(Path.Combine(dest,"python","python.exe"),"-c \"import sys;sys.path.insert(0,'.');import server;db=server.connect();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';db.close();print('OK')\"");
   check.WorkingDirectory=dest;check.UseShellExecute=false;check.CreateNoWindow=true;check.RedirectStandardOutput=true;check.RedirectStandardError=true;
   using(var process=Process.Start(check)){
    string output=process.StandardOutput.ReadToEnd();string error=process.StandardError.ReadToEnd();process.WaitForExit();Log(output+error);
    if(process.ExitCode!=0)throw new Exception("Проверка запуска завершилась ошибкой "+process.ExitCode+". "+error);
   }
   Log("SUCCESS");
   if(!quiet){Shortcut(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory),dest);Shortcut(Environment.GetFolderPath(Environment.SpecialFolder.Programs),dest);if(MessageBox.Show("Установка завершена и проверена.\n\nОткрыть «График поставок» сейчас?","Установка",MessageBoxButtons.YesNo,MessageBoxIcon.Information)==DialogResult.Yes)Process.Start(new ProcessStartInfo(Path.Combine(dest,"График поставок.exe")){UseShellExecute=true});}
   return 0;
  }catch(Exception e){try{Log("ERROR "+e);}catch{}if(!quiet)MessageBox.Show(e.Message+"\n\nЖурнал: "+LogPath,"Ошибка установки",MessageBoxButtons.OK,MessageBoxIcon.Error);return 1;}
 }
 static void Shortcut(string folder,string dest){var type=Type.GetTypeFromProgID("WScript.Shell");dynamic shell=Activator.CreateInstance(type);dynamic shortcut=shell.CreateShortcut(Path.Combine(folder,"График поставок.lnk"));shortcut.TargetPath=Path.Combine(dest,"График поставок.exe");shortcut.WorkingDirectory=dest;shortcut.Save();}
}
