namespace SwarmClone.VRChat.Config;

public class VRChatSettings
{
    public string CoreWsUrl { get; set; } = "ws://127.0.0.1:8765";
    public int OscPort { get; set; } = 9000;
    public string OscAddress { get; set; } = "127.0.0.1";
    public int VrcOscPort { get; set; } = 9001;
    public bool EnableOsc { get; set; } = true;
}
