/*
  Adapted from the Inkplate10_Image_Frame_From_Web example for Soldered Inkplate 10
  https://github.com/SolderedElectronics/Inkplate-Arduino-library/blob/master/examples/Inkplate10/Projects/Inkplate10_Image_Frame_From_Web/Inkplate10_Image_Frame_From_Web.ino

  What this code does:
    1. Connect to a WiFi access point
    2. Retrieve an image from a web address
    3. Display the image on the Inkplate 10 device
    4. (Optional) Check the battery level on the Inkplate device
    5. Set a sleep timer for 60 minutes, and allow the Inkplate to go into deep sleep to conserve battery
*/

// Next 3 lines are a precaution, you can ignore those, and the example would also work without them
#if !defined(ARDUINO_INKPLATE10) && !defined(ARDUINO_INKPLATE10V2)
#error "Wrong board selection for this example, please select e-radionica Inkplate10 or Soldered Inkplate10 in the boards menu."
#endif

#include "Inkplate.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include "battSymbol.h" // Include .h file that contains byte array for battery symbol.

Inkplate display(INKPLATE_3BIT);

const char ssid[] = "";    // Your WiFi SSID
const char *password = ""; // Your WiFi password
const char *imgurl = ""; // Your dashboard image web address

// Battery values
#define BATTV_5 4.1
#define BATTV_4 4.0
#define BATTV_3 3.8
#define BATTV_2 3.6
#define BATTV_1 3.4
#define BATTV_0 3.2

WiFiClientSecure client;

void setup()
{
    Serial.begin(115200);
    display.begin();
    
    // Connect to the WiFi network.
    WiFi.mode(WIFI_MODE_STA);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
    }

    // Join wifi, retrieve image, update display
    char url[256];
    strcpy(url, imgurl);
    Serial.println(display.drawImage(url, display.PNG, 0, 0));

    float voltage = display.readBattery();                   // Read battery voltage
    if (voltage >= BATTV_5) {
      display.drawImage(bat_5, 0, 0, bat_5_w, bat_5_h); // Draw battery symbol
    } else if (voltage >= BATTV_4) {
      display.drawImage(bat_4, 0, 0, bat_4_w, bat_4_h); // Draw battery symbol
    } else if (voltage >= BATTV_3) {
      display.drawImage(bat_3, 0, 0, bat_3_w, bat_3_h); // Draw battery symbol
    } else if (voltage >= BATTV_2) {
      display.drawImage(bat_2, 0, 0, bat_2_w, bat_2_h); // Draw battery symbol
    } else if (voltage >= BATTV_1) {
      display.drawImage(bat_1, 0, 0, bat_1_w, bat_1_h); // Draw battery symbol
    } else {
      display.drawImage(bat_0, 0, 0, bat_0_w, bat_0_h); // Draw battery symbol
    }
    
    display.display();
    
    // Let display go to sleep to conserve battery, and wake up an hour later    
    Serial.println("Going to sleep");
    delay(100);
    esp_sleep_enable_timer_wakeup(60ll * 60 * 1000 * 1000); //wakeup in 60min time - 60min * 60s * 1000ms * 1000us
    esp_deep_sleep_start();
}

void loop()
{
    // Never here, as deepsleep restarts esp32
}
