import pigpio
from flask import Flask, request, jsonify, make_response

LEFT_MOTOR_IN1 = 17
LEFT_MOTOR_IN2 = 27
RIGHT_MOTOR_IN1 = 22
RIGHT_MOTOR_IN2 = 23

pi = pigpio.pi()

for pin in [LEFT_MOTOR_IN1, LEFT_MOTOR_IN2, RIGHT_MOTOR_IN1, RIGHT_MOTOR_IN2]:
    pi.set_PWM_frequency(pin, 50)


def set_motor_speed(motor, speed):
    if not -100 <= speed <= 100:
        raise ValueError("Speed should be between -100 and 100")

    if motor == "left":
        in1 = LEFT_MOTOR_IN1
        in2 = LEFT_MOTOR_IN2
    elif motor == "right":
        in1 = RIGHT_MOTOR_IN1
        in2 = RIGHT_MOTOR_IN2
    else:
        raise ValueError("Invalid motor identifier")

    if speed > 0:
        pi.set_PWM_dutycycle(in1, 2.55 * speed)
        pi.set_PWM_dutycycle(in2, 0)
    elif speed < 0:
        pi.set_PWM_dutycycle(in1, 0)
        pi.set_PWM_dutycycle(in2, -2.55 * speed)
    else:
        pi.set_PWM_dutycycle(in1, 0)
        pi.set_PWM_dutycycle(in2, 0)


app = Flask(__name__)


@app.route("/", methods=["POST", "OPTIONS"])
def slider_data():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    data = request.json
    slider_id = data.get("sliderId")
    value = data.get("value")

    if not slider_id or value is None:
        return jsonify({"message": "Invalid data received"}), 400

    if slider_id in ["left", "right"]:
        set_motor_speed(slider_id, value)

    print(f"Received value {value} from {slider_id}")

    response = jsonify({"message": "Data received successfully"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8000)
    finally:
        pi.stop()
