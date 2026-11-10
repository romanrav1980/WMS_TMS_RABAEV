using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;
using System.Windows.Forms;
class Launcher {
 [STAThread] static int Main(string[] args) {
  string root=AppDomain.CurrentDomain.BaseDirectory; string url="http://127.0.0.1:4379/site/";
  try {
   if(!Ready()) { var start=new ProcessStartInfo(Path.Combine(root,"python","pythonw.exe"),"\""+Path.Combine(root,"start_server.py")+"\"");start.WorkingDirectory=root;start.UseShellExecute=false;start.CreateNoWindow=true;using(var process=Process.Start(start)){for(int i=0;i<60&&!Ready();i++){if(process.HasExited)throw new Exception("Сервер завершился с кодом "+process.ExitCode);Thread.Sleep(250);}} }
   if(!Ready()) throw new Exception("Сервер не запустился. Проверьте, не занят ли порт 4379.");
   if(Array.IndexOf(args,"/check")<0)Process.Start(new ProcessStartInfo(url){UseShellExecute=true});
   return 0;
  } catch(Exception e) {string log=Path.Combine(root,"runtime","launcher.log");try{Directory.CreateDirectory(Path.GetDirectoryName(log));File.AppendAllText(log,DateTime.Now.ToString("s")+" "+e+Environment.NewLine);}catch{}if(Array.IndexOf(args,"/check")<0)MessageBox.Show(e.Message+"\n\nЖурналы: "+log+" и runtime\\server.log","График поставок",MessageBoxButtons.OK,MessageBoxIcon.Error);return 1; }
 }
 static bool Ready(){try{var req=(HttpWebRequest)WebRequest.Create("http://127.0.0.1:4379/api/schedule?chain=drinks");req.Timeout=700;using(var res=(HttpWebResponse)req.GetResponse())using(var r=new StreamReader(res.GetResponseStream()))return res.StatusCode==HttpStatusCode.OK&&r.ReadToEnd().Contains("\"records\"");}catch{return false;}}
}

