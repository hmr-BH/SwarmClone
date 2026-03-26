extends Node

var _current_model: Node = null


func load_model(model_path: String) -> void:
	pass


func execute_action(action_data: Dictionary) -> void:
	if not action_data.has("action_name"):
		return

	var action_name = action_data.action_name
	var params = action_data.get("parameters", {})

	match action_name:
		"wave":
			_play_animation("wave")
		"nod":
			_play_animation("nod")
		"shake_head":
			_play_animation("shake_head")
		"set_expression":
			_set_expression(params.get("expression", "neutral"))
		_:
			push_warning("未知动作: " + action_name)


func _play_animation(anim_name: String) -> void:
	print("播放动画: ", anim_name)


func _set_expression(expression: String) -> void:
	print("设置表情: ", expression)


func set_blend_shape(shape_name: String, value: float) -> void:
	print("设置混合形状: ", shape_name, " = ", value)
