using System.Net;
using System.Text;
using Rug.Osc;

namespace SwarmClone.VRChat.Services;

public class OscService : IDisposable
{
    private readonly int _port;
    private readonly string _address;
    private OscSender? _sender;
    private OscReceiver? _receiver;
    private bool _disposed;

    public event EventHandler<OscMessage>? MessageReceived;

    public OscService(string address, int port)
    {
        _address = address;
        _port = port;
    }

    public void Start()
    {
        _sender = new OscSender(IPAddress.Parse(_address), _port);
        _sender.Connect();

        _receiver = new OscReceiver(IPAddress.Parse(_address), _port + 1);
        _receiver.Connect();

        Task.Run(() => ListenForMessages());
    }

    public void Stop()
    {
        _sender?.Close();
        _receiver?.Close();
    }

    public void SendFloat(string address, float value)
    {
        var message = new OscMessage(address, value);
        _sender?.Send(message);
    }

    public void SendInt(string address, int value)
    {
        var message = new OscMessage(address, value);
        _sender?.Send(message);
    }

    public void SendBool(string address, bool value)
    {
        var message = new OscMessage(address, value);
        _sender?.Send(message);
    }

    private void ListenForMessages()
    {
        while (_receiver?.State == OscSocketState.Connected)
        {
            try
            {
                var packet = _receiver.Receive();
                if (packet is OscMessage message)
                {
                    MessageReceived?.Invoke(this, message);
                }
            }
            catch (Exception)
            {
            }
        }
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;

        Stop();
        _sender?.Dispose();
        _receiver?.Dispose();
    }
}
