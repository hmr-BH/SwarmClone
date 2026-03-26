using System.Net.WebSockets;
using System.Text;
using Newtonsoft.Json;
using SwarmClone.VRChat.Config;
using SwarmClone.VRChat.Models;

namespace SwarmClone.VRChat.Services;

public class WebSocketClient : IDisposable
{
    private readonly VRChatSettings _settings;
    private ClientWebSocket? _webSocket;
    private readonly CancellationTokenSource _cts = new();
    private bool _disposed;

    public event EventHandler<Message>? MessageReceived;

    public bool IsConnected => _webSocket?.State == WebSocketState.Open;

    public WebSocketClient(VRChatSettings settings)
    {
        _settings = settings;
    }

    public async Task ConnectAsync()
    {
        _webSocket = new ClientWebSocket();
        await _webSocket.ConnectAsync(new Uri(_settings.CoreWsUrl), _cts.Token);

        _ = Task.Run(ReceiveMessages);
    }

    public async Task DisconnectAsync()
    {
        if (_webSocket?.State == WebSocketState.Open)
        {
            await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", _cts.Token);
        }
    }

    public async Task SendMessageAsync(Message message)
    {
        if (_webSocket?.State != WebSocketState.Open) return;

        var json = JsonConvert.SerializeObject(message);
        var bytes = Encoding.UTF8.GetBytes(json);
        await _webSocket.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, _cts.Token);
    }

    private async Task ReceiveMessages()
    {
        var buffer = new byte[4096];

        while (_webSocket?.State == WebSocketState.Open && !_cts.Token.IsCancellationRequested)
        {
            try
            {
                var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    var json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    var message = JsonConvert.DeserializeObject<Message>(json);
                    if (message != null)
                    {
                        MessageReceived?.Invoke(this, message);
                    }
                }
            }
            catch (OperationCanceledException)
            {
                break;
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

        _cts.Cancel();
        _webSocket?.Dispose();
        _cts.Dispose();
    }
}
