#!/bin/bash

ngrok http 8082 > /dev/null &
sleep 10s
gen_url=$(curl -s http://127.0.0.1:4040/api/tunnels | jq -r ".tunnels[0].public_url")
twilio phone-numbers:update "+1xxxxxxxxxx" --sms-url="$gen_url/temperature/"
