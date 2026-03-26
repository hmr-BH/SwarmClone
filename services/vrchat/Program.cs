using SwarmClone.VRChat.Config;
using SwarmClone.VRChat.Services;

namespace SwarmClone.VRChat;

class Program
{
    private static VRChatSettings _settings = new();
    private static WebSocketClient? _wsClient;
    private static OscService? _oscService;

    static async Task Main(string[] args)
    {
        Console.WriteLine("启动 VRChat 对接服务...");

        _wsClient = new WebSocketClient(_settings);
        _wsClient.MessageReceived += OnMessageReceived;

        if (_settings.EnableOsc)
        {
            _oscService = new OscService(_settings.OscAddress, _settings.OscPort);
            _oscService.MessageReceived += OnOscMessageReceived;
            _oscService.Start();
            Console.WriteLine("OSC 服务已启动");
        }

        try
        {
            await _wsClient.ConnectAsync();
            Console.WriteLine("已连接到核心服务");
            Console.WriteLine("VRChat 对接服务已启动，按 Ctrl+C 停止");

            await Task.Delay(Timeout.Infinite);
        }
        catch (OperationCanceledException)
        {
            Console.WriteLine("正在停止服务...");
        }
        finally
        {
            await Cleanup();
        }
    }

    private static void OnMessageReceived(object? sender, Models.Message message)
    {
        Console.WriteLine($"收到消息: {message.Type}");

        if (message.Type == "action" && message is Models.ActionMessage actionMsg)
        {
            HandleAction(actionMsg);
        }
    }

    private static void OnOscMessageReceived(object? sender, Rug.Osc.OscMessage message)
    {
        Console.WriteLine($"收到 OSC 消息: {message.Address}");
    }

    private static void HandleAction(Models.ActionMessage action)
    {
        Console.WriteLine($"执行动作: {action.ActionName}");

        if (_oscService == null) return;

        var paramName = $"/avatar/parameters/{action.ActionName}";

        if (action.Parameters.TryGetValue("value", out var value))
        {
            switch (value)
            {
                case float f:
                    _oscService.SendFloat(paramName, f);
                    break;
                case int i:
                    _oscService.SendInt(paramName, i);
                    break;
                case bool b:
                    _oscService.SendBool(paramName, b);
                    break;
            }
        }
    }

    private static async Task Cleanup()
    {
        _oscService?.Dispose();
        if (_wsClient != null)
        {
            await _wsClient.DisconnectAsync();
            _wsClient.Dispose();
        }
    }
}
