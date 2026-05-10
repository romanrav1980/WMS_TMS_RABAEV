using System;
using System.Collections.Generic;
using System.Text;

using System.Net;
using System.Net.Sockets;
using System.Threading;


namespace MCSSTestNet
{
    /// <summary>
    /// Socket notification events.
    /// </summary>
    public enum NotifyEvents
    {
        Connected,
        DataSent,
        DataReceived,
        Disconnected,
        ConnectError,
        SendError,
        ReceiveError,
        DisconnectError,
        OtherError
    }

    // Socket communications will be done asynchronously
    public class DeviceSocket
    {
        // The Socket class provides a rich set of methods and properties for network communications via sockets. 
        // Although Socket class supports both synchronous and asynchronous data transfers, we choose asynchronous 
        // method here
        public Socket mySocket = null;

        // Used to synchronize the shutdown process, terminate
        // any pending async calls before Disconnect returns
        ManualResetEvent asyncEvent = new ManualResetEvent(true);

        // private string terminator = "<END_OF_RECORD>";

        public string receiveBuf = null;
        private const int BUFFER_SIZE = 1024;

        // notification event
        public delegate void NotifyEventHandler(NotifyEvents nEvent, object data);
        public event NotifyEventHandler Notify;

        // Closing flag
        private bool closing = false;
        byte[] bRcvd = new byte[BUFFER_SIZE];

        /// <summary>
        /// Connect to the specified address and port number.
        /// </summary>
        public void Connect(String ip, int port)
        {
            // Create a socket object
            // The addressFamily parameter (Address for IP version 4) specifies the addressing scheme the Socket class 
            // The socketType parameter specifies the type of the Socket class
            // The protocolType parameter (tcp - Transmission Control Protocol) specifies the protocol used by Socket
            mySocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

            // Sets the state of the event to nonsignaled, causing threads to block
            asyncEvent.Reset();

            // Prepare for async connection
            IPAddress ipAddress = IPAddress.Parse(ip);
            IPEndPoint ipEndPoint = new IPEndPoint(ipAddress, port);

            // Begins an asynchronous request for a remote host connection
            mySocket.BeginConnect(ipEndPoint, new AsyncCallback(OnConnect), null);

            // wait for any async operations to complete
            asyncEvent.WaitOne();
        }

        /// <summary>
        /// The property Socket.Connected does not always indicate if the socket is currently 
        /// connected, this polls the socket to determine the latest connection state.
        /// 
        /// Returns True or False
        /// </summary>
        public bool IsConnected
        {
            get
            {
                if (mySocket == null)   return false;

                // the socket is not connected if the Connected property is false
                if (!mySocket.Connected)    return false;

                // there is no guarantee that the socket is connected even if the
                // Connected property is true
                try
                {
                    // poll for error to see if socket is connected
                    return !mySocket.Poll(1, SelectMode.SelectError);
                }
                catch
                {
                    return false;
                }
            }
        }

        /// <summary>
        /// Async connect callback
        /// </summary>
        private void OnConnect(IAsyncResult ar)
        {
            try
            {
                // Ends a pending asynchronous connection request
                mySocket.EndConnect(ar);

                // Assert: Connected. Notify the app.
                NotifyCaller(NotifyEvents.Connected, null);
            }
            catch (Exception ex)
            {
                NotifyCaller(NotifyEvents.ConnectError, ex.Message);
            }
        }

        /// <summary>
        /// Disconnect a connected socket
        /// </summary>
        public void Disconnect()
        {
            // if the socket is not created
            if (mySocket == null) return;

            closing = true;

            try
            {
                // first, shutdown the socket
                mySocket.Shutdown(SocketShutdown.Both);
            }
            catch { }

            try
            {
                // next, close the socket which terminates any pending
                // async operations
                mySocket.Close();

                // wait for any async operations to complete
                asyncEvent.WaitOne();
            }
            catch { }

            closing = false;

        }

		/// <summary>
		/// Send data to the server.
		/// </summary>
        public void Send(String data)
        {
            try
            {
                // String must be converted to byet[]
                byte[] byteArray = new UnicodeEncoding().GetBytes(data);

                // Send the data to the connected socket
                // mySocket.BeginSend(byteArray, 0, byteArray.Length, SocketFlags.None, null, null);
                
                //mySocket.BeginSend(byteArray, 0, byteArray.Length, SocketFlags.None, new AsyncCallback(OnSend), null);
                mySocket.Send(byteArray, byteArray.Length,0 );

                //asyncEvent.Reset();
                //===================================================
                // Receive the server home page content.
                int bytes = 0;
                string page="" ;
                Byte[] bytesReceived = new byte[256];

                // The following will block until te page is transmitted.
                do
                {
                    bytes = mySocket.Receive(bytesReceived, bytesReceived.Length, 0);
                    page = page + Encoding.Unicode.GetString(bytesReceived, 0, bytes);
                }
                while (bytes > 0);

                //===================================================

            }
            catch (Exception ex)
            {
                NotifyCaller(NotifyEvents.SendError, ex.Message);
            }

        }

        /// <summary>
        /// Async send callback
        /// </summary>
        private void OnSend(IAsyncResult ar)
        {
            try
            {
                mySocket.EndSend(ar);

                // ASSERT: Data sent successfully
                NotifyCaller(NotifyEvents.DataSent, null);
            }
            catch (Exception ex)
            {
                NotifyCaller(NotifyEvents.SendError, ex.Message);
            }
        }

		/// <summary>
		/// Receive data from the server.
		/// </summary>
        public void Receive()
        {
            try
            {
                asyncEvent.Reset();

                mySocket.BeginReceive(bRcvd, 0, BUFFER_SIZE, SocketFlags.None, new AsyncCallback(OnReceive), null);

                //Thread.Sleep(1000);
            }
            catch (Exception ex)
            {
                NotifyCaller(NotifyEvents.ReceiveError, ex.Message);
            }
        }

        /// <summary>
        /// Async send callback
        /// </summary>
        private void OnReceive(IAsyncResult ar)
        {
            try
            {
                int len = mySocket.EndReceive(ar);
                receiveBuf = UnicodeEncoding.Unicode.GetString(bRcvd, 0, len);

                // ASSERT: Data receieved successfully
                NotifyCaller(NotifyEvents.DataReceived, receiveBuf);
            }
            catch (Exception ex)
            {
                NotifyCaller(NotifyEvents.ReceiveError, ex.Message);
            }
        }

        /// <summary>
        /// Notify the app
        /// </summary>
        private void NotifyCaller(NotifyEvents nEvent, object data)
        {
            // the async operation has completed
            asyncEvent.Set();

            // don't raise notification events when disconnecting
            if ((this.Notify != null) && !closing)
                Notify(nEvent, data);
        }

    }
}
