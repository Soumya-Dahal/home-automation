from machine import Pin
import time

# Configuration for stepper motor
TRIG_PIN = 17  
ECHO_PIN = 16

#Configuration for LED
LED_PIN = 14

#Initialize Stepper Motor
trig = Pin(TRIG_PIN,Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Stepper motor pins
in1 = 10
in2 = 11
in3 = 12
in4 = 13

# Constants
DISTANCE_THRESHOLD = 50  # cm
STEP_DELAY = 2  # ms
STEPS_PER_REVOLUTION = 1024

pins = [
            Pin(in1, Pin.OUT),
            Pin(in2, Pin.OUT),
            Pin(in3, Pin.OUT),
            Pin(in4, Pin.OUT)
        ]
#Half sequence of stepper motor
sequence = [
                 [1, 0, 0, 0],
                 [1, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 1, 0],
                 [0, 0, 1, 0],
                 [0, 0, 1, 1],
                 [0, 0, 0, 1],
                 [1, 0, 0, 1]
        ]

    
def rotate_motor(steps, direction=1):
    current_step = 0
    for _ in range(steps):
        if direction == 1:
            current_step = (current_step + direction) % len(sequence)
        else:
            current_step = (current_step -1 + len(sequence))%len(sequence)
            
        current_pattern = sequence[current_step]   
        for i in range (len(pins)):
            pins[i].value(current_pattern[i])
            
        time.sleep_ms(STEP_DELAY)

    
def stop_motor():
    for pin in pins:
        pin.value(0)

    
def measure_distance():
    try:
        trig.value(0)
        time.sleep_us(2)
        
        #Trigger the sensor
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)
        
        while echo.value()==0:
            pass
        trigger_time=time.ticks_us()
        
        while echo.value()==1:
            pass
        received_time=time.ticks_us()
        time_diff=received_time-trigger_time
        distance = (time_diff*0.03432)/2
        return distance
        
    except Exception as e:
        print(f"Sensor error: {e}")
        return None

# Initialize LED and door condition
led = Pin(LED_PIN, Pin.OUT)
door_status = 0
    
def main():
    global door_status
    print("Distance sensing system started.")
    print(f"Motor will activate when distance < {DISTANCE_THRESHOLD} cm")
    
    while True:
        try:
            distance = measure_distance()
            
            if distance is None:
                print("Measurement timeout")
            else:
                print(f"Distance: {distance:.2f} cm")
                if distance < DISTANCE_THRESHOLD and door_status==0:
                    led.value(1)
                    print("Object detected, opening door")
                    rotate_motor(STEPS_PER_REVOLUTION,-1)
                    stop_motor()
                    door_status = 1
                    continue
                elif distance>=DISTANCE_THRESHOLD and door_status==1:
                    led.value(0)
                    print("Closing door")
                    rotate_motor(STEPS_PER_REVOLUTION,1)
                    stop_motor()  
                    door_status=0
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"Error: {e}")
            stop_motor()
            led.value(0)
            time.sleep(1)

# Run the program
if __name__ == "__main__":
    main()

