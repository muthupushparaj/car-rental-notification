#include <iostream>
#include <string>

//The Strategy Pattern is used to define different strategies for sending notifications (Firebase or AWS) and allows them to be//i used interchangeably.
//The NotificationService interface acts as the "Strategy" interface, and FirebaseNotification and AWSNotification are the concrete strategies.
//By passing an instance of a NotificationService to CarRental, we can change the notification behavior at runtime without modifying the CarRental class.


enum class NotificationType 
{
    Firebase,
    AWS
};

void sendNotification(NotificationType type, const std::string& message)
{
    if (type == NotificationType::Firebase)
    {
        std::cout << "[Firebase Notification] " << message << std::endl;
    }
    else if (type == NotificationType::AWS)
    {
        std::cout << "[AWS Notification] " << message << std::endl;
    }
}

class CarRental
{
public:
    CarRental(int carId, int maxSpeed, NotificationType notificationType)
        : carId(carId), maxSpeed(maxSpeed), notificationType(notificationType) {}

    void monitorSpeed(int currentSpeed)
    {
        if (currentSpeed > maxSpeed)
        {
            std::cout << "[Alert] Car ID: " << carId
                      << " - Speed limit exceeded! Current Speed: " << currentSpeed
                      << " km/h, Max Speed: " << maxSpeed << " km/h" << std::endl;
            notifyRentalCompany();
        }
    }

private:
    int carId;
    int maxSpeed;
    NotificationType notificationType;

    void notifyRentalCompany()
    {
        std::string message = "Car ID: " + std::to_string(carId) + " exceeded speed limit of " + std::to_string(maxSpeed) + " km/h.";
        sendNotification(notificationType, message);
    }
    
};

class TelematicsDevice 
{
public:
    TelematicsDevice()
    {
        // Seed the random number generator for simulated data
        srand(time(NULL));
    }

    int readSpeedData()
    {
         // Generate a random speed between 0 and 100
    return rand() % 101;
    }
};


// Main function demonstrating functionality
int main()
{
    CarRental car1(101, 80, NotificationType::Firebase);  // Car ID: 101, Max Speed: 80 km/h
    CarRental car2(102, 90, NotificationType::AWS);  
    
    TelematicsDevice device;

    
   while (true) 
   {
        // Read and print speed data
    int current_speed=device.readSpeedData();
    
    std::cout << "car speed value "<< current_speed << std::endl;
    
    car1.monitorSpeed(current_speed);  // Exceeds limit, triggers Firebase notification and alert
    
   }
   

    return 0;
}

