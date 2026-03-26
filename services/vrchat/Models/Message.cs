using Newtonsoft.Json;

namespace SwarmClone.VRChat.Models;

public class Message
{
    [JsonProperty("type")]
    public string Type { get; set; } = string.Empty;

    [JsonProperty("source")]
    public string Source { get; set; } = "vrchat-service";

    [JsonProperty("target")]
    public string? Target { get; set; }

    [JsonProperty("data")]
    public Dictionary<string, object> Data { get; set; } = new();
}

public class ActionMessage : Message
{
    public ActionMessage()
    {
        Type = "action";
    }

    [JsonProperty("action_name")]
    public string ActionName { get; set; } = string.Empty;

    [JsonProperty("parameters")]
    public Dictionary<string, object> Parameters { get; set; } = new();
}

public class AvatarParameter
{
    [JsonProperty("name")]
    public string Name { get; set; } = string.Empty;

    [JsonProperty("value")]
    public object Value { get; set; } = new();

    [JsonProperty("type")]
    public string ParameterType { get; set; } = "float";
}
