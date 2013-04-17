#appengine-apns-gcm#

A unified push service for iPhone and Android push notifications that runs on Google App Engine (GAE). This can be used as an alternative to Urban Airship if all you are doing is basic push notifications.

##need help##
The project runs as-is.. but it was put together really quickly. I will be working on cleaning it up, but I'm looking for other people who would be interested in helping make this project rock solid.  Thanks!

##how to deploy##
1. Clone or download this project
2. Create a new app engine project id at http://appengine.google.com
3. Enable billing on your new project (required for iOS push support)
4. Create a new project in the Google API Console (https://code.google.com/apis/console/) note your new project id in the url
5. Deal with the pain of setting up a new app and creating a push certificate in the Apple developer console
6. Create a new server key for your project in the Google API Console
7. Enable the Google Cloud Messaging API in the Google API Console
8. Edit the app.yaml file to replace application: gae-apns-gcm with your new application name
9. Create a new project in the App Engine Launcher and point it to the appengine project you got here
10. Deploy your new project
11. Insert your new project URL in the iOS and Android sample apps
12. Enter your Project ID in the Android sample app (found in the URL of the Google API Console)
13. Go to http://your-app-id.appspot.com/admin/config
14. Enter your GCM API Key from the Google API Console
15. Enter your push certificate information for iOS (export your push certificate to a .pem file, and copy the certificate and private key and paste it here. Include the -----BEGIN/END CERTIFICATE----- and -----BEGIN/END PRIVATE KEY-----

##now what?##
1. Launch your sample iOS and Android apps to enable push on your devices
2. Send an HTTP POST to send a push notification to all your devices

```HTTP POST http://your-app-id.appspot.com/push/broadcast --> message={"request":{"data":{"custom": "json data"},"platforms": [1,2], "ios_message":"This is a test","ios_button_text":"yeah!","ios_badge": -1, "ios_sound": "soundfile", "android_collapse_key": "collapsekey"}}
```