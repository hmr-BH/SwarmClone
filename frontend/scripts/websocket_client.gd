extends Node

signal connected()
signal disconnected()
signal message_received(message: Dictionary)

var _socket: WebSocketPeer = WebSocketPeer.new()
var _url: String = ""
var _is_connected: bool = false


func connect_to_server(url: String) -> void:
	_url = url
	var err = _socket.connect_to_url(url)
	if err != OK:
		push_error("WebSocket 连接失败: " + str(err))


func disconnect_from_server() -> void:
	_socket.close(1000, "Client disconnecting")
	_is_connected = false


func send_message(message: Dictionary) -> void:
	if _is_connected:
		var json = JSON.stringify(message)
		_socket.send_text(json)


func _process(_delta: float) -> void:
	_socket.poll()

	var state = _socket.get_ready_state()

	match state:
		WebSocketPeer.STATE_OPEN:
			if not _is_connected:
				_is_connected = true
				connected.emit()

			while _socket.get_available_packet_count() > 0:
				var packet = _socket.get_packet()
				var text = packet.get_string_from_utf8()
				var json = JSON.new()
				if json.parse(text) == OK:
					message_received.emit(json.data)

		WebSocketPeer.STATE_CLOSED:
			if _is_connected:
				_is_connected = false
				disconnected.emit()

		WebSocketPeer.STATE_CONNECTING:
			pass

		WebSocketPeer.STATE_CLOSING:
			pass


func is_connected_to_server() -> bool:
	return _is_connected
