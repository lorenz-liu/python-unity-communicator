using UnityEngine;
using System;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

public class PortCommunicator : MonoBehaviour
{
    public string pythonServerAddress = "127.0.0.1";
    public int pythonServerPort = 12345;

    private bool _isCommunicationInProgress; // Flag to track communication

    public async void SendDataToPython()
    {
        if (_isCommunicationInProgress)
        {
            Debug.Log("Communication is already in progress. Please wait.");
            return;
        }

        try
        {
            // Set the flag to indicate that communication is in progress
            _isCommunicationInProgress = true;

            const string message = "TRIGGERED";
            Debug.Log("From Unity: " + message);
            var data = Encoding.UTF8.GetBytes(message);

            var response = await Task.Run(() => SendAndReceiveData(data));

            Debug.Log($"Received response from Python: {response}");
        }
        catch (Exception e)
        {
            Debug.LogError($"Error: {e}");
        }
        finally
        {
            // Reset the flag when communication is complete
            _isCommunicationInProgress = false;
        }
    }

    private string SendAndReceiveData(byte[] data)
    {
        try
        {
            using var client = new TcpClient(pythonServerAddress, pythonServerPort);
            using var stream = client.GetStream();
            stream.Write(data, 0, data.Length);

            var responseBuffer = new byte[1024];
            var bytesRead = stream.Read(responseBuffer, 0, responseBuffer.Length);
            return Encoding.UTF8.GetString(responseBuffer, 0, bytesRead);
        }
        catch (Exception e)
        {
            Debug.LogError($"Error: {e}");
            return "Error, please do remember to run PythonClient.py synchronously! ";
        }
    }
}