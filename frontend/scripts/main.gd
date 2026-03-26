extends Node

var websocket_client: Node
var model_controller: Node


func _ready() -> void:
	websocket_client = $WebSocketClient
	model_controller = $ModelController

	websocket_client.message_received.connect(_on_message_received)

	websocket_client.connect_to_server("ws://127.0.0.1:8765")


func _on_message_received(message: Dictionary) -> void:
	if message.has("type"):
		match message.type:
			"action":
				model_controller.execute_action(message)


func _process(_delta: float) -> void:
	pass
