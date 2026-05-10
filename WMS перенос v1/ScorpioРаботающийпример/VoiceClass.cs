using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace MCSSTestNet
{
    class VoiceClass
    {
        public string voice_folder = "\\Flash Disk\\monetka\\irina\\";

        [DllImport("coredll", EntryPoint = "PlaySoundW", SetLastError = false)]
        private extern static bool PlaySoundW(String lpszName, IntPtr hModule, uint dwFlags);

        #region Разговоры

        public enum PlaySoundFlags : int
        {
            SND_SYNC = 0x0,     // play synchronously (default)
            SND_ASYNC = 0x1,    // play asynchronously
            SND_NODEFAULT = 0x2,    // silence (!default) if sound not found
            SND_MEMORY = 0x4,       // pszSound points to a memory file
            SND_LOOP = 0x8,     // loop the sound until next sndPlaySound
            SND_NOSTOP = 0x10,      // don't stop any currently playing sound
            SND_NOWAIT = 0x2000,    // don't wait if the driver is busy
            SND_ALIAS = 0x10000,    // name is a registry alias
            SND_ALIAS_ID = 0x110000,// alias is a predefined ID
            SND_FILENAME = 0x20000, // name is file name
            SND_RESOURCE = 0x40004, // name is resource name or atom
        }


        private void PlaySound1( string filepath )
        {
            try
            {
                MessageBox.Show(filepath);
                PlaySoundW( filepath , IntPtr.Zero, (int)(PlaySoundFlags.SND_FILENAME | PlaySoundFlags.SND_SYNC));
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }
        #endregion
        
        public void VOICE_say_number(long m_number)
        {

            if (m_number > 9999)
            {
                return;
            }

            string m_numbers = Convert.ToString(m_number);
            if (m_numbers.Length >= 4)
            { // Количество тысяч
                string kt = m_numbers.Substring(0, 1);
                PlaySound1( voice_folder + kt + "000.wav" );
            }

            if (m_numbers.Length >= 3)
            { // Количество тысяч
                string kt = m_numbers.Substring(1, 1);
                PlaySound1(  voice_folder + kt + "00.wav" );
                 
            }


            if (m_numbers.Length >= 2)
            { // Количество тысяч
                string kt = m_numbers.Substring(2, 1);
                 PlaySound1( voice_folder + kt + "0.wav" ) ;
                
            }


            if (m_numbers.Length >= 1)
            { // Количество тысяч
                string kt = m_numbers.Substring(3, 1);
                PlaySound1(  voice_folder + kt + ".wav");
               
            }




        }

        bool IsNumber(string s)
        {
            try
            {
                if (Convert.ToInt32(s) > 0)
                {
                    return true;
                }
            }
            catch { }
            return false;
        }

        public void SayWord(string word)
        {
            //  VOICE_say_number(9876);

            string str1 = "";
            str1 = word;
            try
            {
                foreach (string m_sline in word.Split('.'))
                {
                    MessageBox.Show(m_sline);
                    if (!IsNumber(m_sline))
                    {
                        PlaySound1(voice_folder + m_sline + ".wav");
                    }
                    else
                    {
                        VOICE_say_number(Convert.ToInt32(m_sline));
                    }

                }
            }
            catch (Exception ex)
            { 
                
            }

        }




    }
}
