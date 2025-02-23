# Digital-Twin-Security-IoT
This is experiment aiming to get utmost security ,ensured taken to secure digital twin of IoT systems 

starting docker: 
```
docker-compose up -d
```
To run pocilies
```
 curl -X PUT 'http://localhost:8080/api/2/policies/my.test:policy' -u 'ditto:ditto' -H 'Content-Type:application/json' -d @policy.json

```
expected output:                                                                                          
{"policyId":"my.test:policy","imports":{},"entries":{"owner":{"subjects":{"nginx:ditto":{"type":"nginx basic auth user"}},"resources":{"thing:/":{"grant":["READ","WRITE"],"revoke":[]},"policy:/":{"grant":["READ","WRITE"],"revoke":[]},"message:/":{"grant":["READ","WRITE"],"revoke":[]}},"importable":"implicit"},"connection":{"subjects":{"connection:hivemq-mqtt":{"type":"Connection to HiveMQ MQTT broker"}},"resources":{"thing:/":{"grant":["READ","WRITE"],"revoke":[]},"message:/":{"grant":["READ","WRITE"],"revoke":[]}},"importable":"implicit"},"observer":{"subjects":{"ditto:observer":{"type":"observer user"}},"resources":{"thing:/features":{"grant":["READ"],"revoke":[]},"policy:/":{"grant":["READ"],"revoke":[]},"message:/":{"grant":["READ"],"revoke":[]}},"importable":"implicit"}}}

to add things to this 

And create these two things in Ditto: 

```
curl -X PUT 'http://localhost:8080/api/2/things/my.sensors:sensor01' -u 'ditto:ditto' -H 'Content-Type: application/json' -d @sensor01.json
```
```
curl -X PUT 'http://localhost:8080/api/2/things/my.sensors:sensor02' -u 'ditto:ditto' -H 'Content-Type: application/json' -d @sensor02.json
```
