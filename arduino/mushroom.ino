// Include libraries
#include <Wire.h>
#include <Adafruit_AM2315.h>
#include <TimerOne.h>

// Setup the pins
#define CO2_PIN (0) // Analog 0 pin
// Fogger box
#define shftOutClkPin 12
#define shftOutLtchPin 10
#define shftOutDataPin 11
// Powertail
int PSSR1 = 9;

// Define some variables
Adafruit_AM2315 am2315;
float celsius;
float farenheit;
float humidity;
float CO2;
int numOfFoggers = 10;
byte shftOutValue = 0;
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

// CO2 Sensor variables
#define READ_SAMPLE_INTERVAL (50) //define how many samples you are going to take in normal operation
#define READ_SAMPLE_TIMES    (5)  //define the time interval(in milisecond) between each samples in 
float v400ppm = 3.670;   // From calibration in my living room
float v40000ppm = 2.050; // Attempted calibration ( http://www.veetech.org.uk/Prototype_CO2_Monitor.htm )
float deltavs = v400ppm - v40000ppm;
float A = deltavs/(log10(400) - log10(40000));
float B = log10(400);

// Powertail variables
volatile int i=0;               // Variable to use as a counter
volatile boolean zero_cross=0;  // Boolean to store a "switch" to tell us if we have crossed zero
int fanPercent = 0;
int freqStep = 60;              // freq of main

// Setup method
void setup() {
  //Serial.begin(9600);
  Serial.begin(115200);
  Serial.println("Starting the farm");
  
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

  // Setup fogger pins
  pinMode(shftOutLtchPin, OUTPUT);
  pinMode(shftOutClkPin, OUTPUT);
  pinMode(shftOutDataPin, OUTPUT);
  
  // Setup powertail and zero_cross_detect
  pinMode(PSSR1, OUTPUT);
  attachInterrupt(0, zero_cross_detect, RISING);   // Attach an Interupt to Pin 2
  Timer1.initialize(freqStep);
  Timer1.attachInterrupt(fan_check,freqStep);
  
  // Make sure we have the AM2315 connected
  if (! am2315.begin()) {
     Serial.println("Sensor not found, check wiring & pullups!");
     while (1);
  }
}

// Main loop
void loop()
{
  // print the string when a newline arrives:
  if (stringComplete)
  {
    //Serial.print("INPUT: ");
    //Serial.println(inputString);   
    if ( inputString == "poll" || inputString == "POLL" )
    {
      poll();
    }
    else if ( inputString.startsWith("set foggers") || inputString.startsWith("SET FOGGERS") )
    {
      numOfFoggers = inputString.substring(12,14).toInt();
      Serial.print("set foggers to: ");
      Serial.println(numOfFoggers);
    }
    else if ( inputString.startsWith("set fan") || inputString.startsWith("SET FAN") )
    {
      fanPercent = inputString.substring(8,11).toInt();
      Serial.print("set fan to: ");
      Serial.println(fanPercent);
    }
    inputString = "";
    stringComplete = false;
  }
  foggers();
}

void poll()
{
  pollTemperature();
  CO2 = pollCO2();
  Serial.print(humidity);
  Serial.print(";");
  Serial.print(celsius);
  Serial.print(";");
  Serial.print(farenheit);
  Serial.print(";");
  Serial.print(CO2);
  Serial.print(";");
  Serial.print(numOfFoggers);
  Serial.print(";");
  Serial.print(fanPercent);
  Serial.println();
}

void pollTemperature()
{
  // Read the temperature and humidity from the AM2315
  am2315.readTemperatureAndHumidity(celsius,humidity);
  farenheit = Celsius2Fahrenheit(celsius);    
}

float pollCO2()
{
  int i;
  float v=0;

  for (i=0;i<READ_SAMPLE_TIMES;i++) {
    v += analogRead(CO2_PIN);
    delay(READ_SAMPLE_INTERVAL);
  }
  // Convert to voltage
  v = (v/READ_SAMPLE_TIMES)/204.6; // I got 204.6 from them WTF?
  // Calculate co2 from log10 formula (see sensor datasheet)
  return pow(10, ((v - v400ppm)/A) + B );
}

void foggers()
{  
  // Hold down the latch
  digitalWrite(shftOutLtchPin, LOW);
  
  // Clear the pins
  digitalWrite(shftOutDataPin, 0);
  digitalWrite(shftOutClkPin, 0);
  
  int i=0;
  int pinState;
  // Do 15 because there are 16 pins on the registers
  for (i=15; i>=0; i--)
  {
    digitalWrite(shftOutClkPin, 0);
    
    // If the value is less than number of foggers we will turn on the pin
    if ( i < numOfFoggers )
    {
      pinState = 1; // 1 means it is on
    } else {
      pinState = 0; // 0 means it is off
    }
    
    digitalWrite(shftOutDataPin, pinState);
    //register shifts bits on upstroke of clock pin  
    digitalWrite(shftOutClkPin, 1);
    //zero the data pin after shift to prevent bleed through
    digitalWrite(shftOutDataPin, 0);
  }
  // Unlatch to light up the changes
  digitalWrite(shftOutLtchPin, HIGH); 
}  

// Powertail method. Fired by the timer
void fan_check()
{
 if ( fanPercent >= 100 )
 {
   digitalWrite(PSSR1, HIGH);  // Full ON
 } else if ( fanPercent <= 0 )
 {
   digitalWrite(PSSR1,LOW);    // Full OFF
 } else {
   if (zero_cross == 1) // Make sure we are at a zero-cross point
   {
    /*
      10 = full on... 11 high speed to 109 slowest ... > 110 off
      because 10 is the base delay subtrace percent from 110;
    */
    if ( i >=(110 - fanPercent) ) // 10 is the base delay so subtrack he percent from 110
    {
      delayMicroseconds(100);
      digitalWrite(PSSR1, HIGH);
      delayMicroseconds(50);
      digitalWrite(PSSR1, LOW);
      i = 0;
      zero_cross = 0; // Reset the zero_cross so it may be turned on again at the next zero_cross_detect    
     } else {
       i++; // If the dimming value has not been reached, increment the counter
     }
   }
 }
}

void zero_cross_detect() 
{
   zero_cross = 1;  // set the boolean to true that a zero cross has occured
} 

float Celsius2Fahrenheit(float celsiusIn)
{
  return 1.8 * celsiusIn + 32;
}

// Event to handle the serial input
void serialEvent()
{
  while (Serial.available())
  {
    char inChar = (char)Serial.read();
    // if the incoming character is a ; set a flag so the main loop can do something about it:
    if (inChar == ';' || inChar == '\n')
    { 
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}
