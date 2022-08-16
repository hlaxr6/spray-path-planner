extends MeshInstance

const IS_MOVING_FORWARD = 0
const IS_STOPPED = 1
const IS_MOVING_BACKWARD = 2
const SCALE = Vector3(.3,.3,.3)

var movingDirection = IS_MOVING_FORWARD
var activePoint = 0
var deltaCount = 0

func _ready():
	set_process(true)

func _process(delta):
	var pathNode = get_parent()
	var currentPoint = {}
	currentPoint["position"] = pathNode.get_point_vector(activePoint)
	currentPoint["rotation"] = pathNode.get_nozzle_rotation_vector(activePoint)
	var nextPoint =  {}
	nextPoint["position"] = pathNode.get_point_vector(activePoint+1)
	nextPoint["orientation"] = pathNode.get_nozzle_rotation_vector(activePoint+1)

	set_position(currentPoint, nextPoint)
	increment_delta(delta, pathNode)

func increment_delta(delta, pathNode):
	var length = get_parent().get_length_at_point(activePoint)
	var dtime = get_parent().get_time(activePoint+1) - get_parent().get_time(activePoint)
	if movingDirection == IS_MOVING_FORWARD:
		deltaCount += delta * (1/dtime)/2
		if deltaCount > 1:
			deltaCount = 0
			activePoint += 1
		elif activePoint >= pathNode.numberOfPositions - 2:
			activePoint = 0
	elif movingDirection == IS_MOVING_BACKWARD:
		deltaCount -= delta * (1/length)
		if deltaCount <= 0:
			deltaCount = 1
			activePoint -= 1
		if activePoint < 0:
			activePoint = pathNode.numberOfPositions - 2

func get_active_point():
	return activePoint

func set_position_from_slider(activePointPassed, deltaPassed):
	activePoint = activePointPassed
	deltaCount = deltaPassed

func set_move_forward():
	movingDirection = IS_MOVING_FORWARD

func set_move_backward():
	movingDirection = IS_MOVING_BACKWARD

func set_stop_moving():
	movingDirection = IS_STOPPED

func set_position(currentPoint, nextPoint):
	var pos = currentPoint["position"].linear_interpolate(nextPoint["position"], deltaCount)
	set_look_at(currentPoint)
	set_translation(pos)
	set_scale(SCALE)

func set_look_at(currentPoint):
	look_at_from_pos(currentPoint["position"], currentPoint["rotation"], Vector3(0,1,0))