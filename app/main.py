import json
from flask import Flask, render_template, request, jsonify, session
from flask_mqtt import Mqtt


app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'
app.config['MQTT_BROKER_PORT'] = 1883
# Set this item when you need to verify username and password
app.config['MQTT_USERNAME'] = 'admin'
# Set this item when you need to verify username and password
app.config['MQTT_PASSWORD'] = 'admin'
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
# If your broker supports TLS, set it True
app.config['MQTT_TLS_ENABLED'] = False
topic = 'calculator/values'

app.secret_key = 'siemens-task'

mqtt_client = Mqtt(app)

# Values for the calculation
a_value = None
b_value = None


@app.route('/')
def main():
    session['a_value'] = a_value
    session['b_value'] = b_value
    return render_template('main.html', a=a_value, b=b_value)


@mqtt_client.on_connect()
# Subscribe to topic after successfully connecting
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic)  # subscribe topic
    else:
        print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    global a_value, b_value
    # init dictionary with data
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    # redirect values to main.html
    payload_dict = json.loads(data['payload'])
    a_value = payload_dict['a']
    b_value = payload_dict['b']

    # publish result value
    result = int(a_value) + int(b_value)
    mqtt_client.publish("calculator/add/result", result)


# run application on port 5000, debug mod for reloading
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
