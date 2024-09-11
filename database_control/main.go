package main

import (
	"fmt"
	"log"
	"os"

	"database_control/db_connector"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/spf13/viper"
)

func logConfigValues() {
	log.Println("Config values for database:")
	if databaseConfig, ok := viper.AllSettings()["database"].(map[string]interface{}); ok {
		for key, val := range databaseConfig {
		    if key == "password"{
		        log.Printf("**************\n")
		    }else{
		        log.Printf("%v = %v\n", key, val)
		    }
		}
	} else {
		log.Fatalln("No database config found.")
	}

	log.Println("Config values for api_config:")
	if apiConfig, ok := viper.AllSettings()["api_config"].(map[string]interface{}); ok {
		for key, val := range apiConfig {
			log.Printf("%v = %v\n", key, val)
		}
	} else {
		log.Fatalln("No api_config config found.")
	}
}

func setDefaultConfig() {
	viper.SetDefault("api_config.host", "127.0.0.1")
	viper.SetDefault("api_config.port", 6000)

	// set default for the DATABASE
	viper.SetDefault("database.database_name", "szymon")
	viper.SetDefault("database.host", "localhost")
	viper.SetDefault("database.port", 5433)
	viper.SetDefault("database.user", "szymon")
	// encryption!
	viper.SetDefault("database.password", "****")
	viper.SetDefault("database.sslmode", false)
}

func main() {
	// logger setup
	file, err := os.OpenFile("database_api_logs.log", os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	defer file.Close()
	// set output file for logging
	log.SetOutput(file)

	// config loading
	viper.SetConfigFile("database_api_config.yaml")
	viper.SetConfigType("yaml")

	// load in config values
	err = viper.ReadInConfig()
	if err != nil {
		log.Fatalf("Error reading config file: %v", err)
	}

	// set defaults for API
	setDefaultConfig()
	// log config values
	logConfigValues()

	// start fiber app
	app := fiber.New()
	// adding logging file for the fiber app
	app.Use(logger.New(logger.Config{
		Output: file,
	}))

	// open database connection
	db := db_connector.NewDB(
		viper.GetString("database.database_name"),
		viper.GetString("database.host"),
		viper.GetString("database.user"),
		viper.GetString("database.password"),
		viper.GetInt("database.port"),
		viper.GetBool("database.sslmode"))

	db.Open()
	log.Println("Creating new database connection")

	// add an endpoint
	app.Post("/database", func(c *fiber.Ctx) error {
		var question db_connector.Question

		// retrieve
		if err := c.BodyParser(&question); err != nil {
			log.Println("Invalid JSON received by the API")
			return c.Status(fiber.StatusBadRequest).SendString("Invalid JSON")
		}
		// will be logged!
		log.Printf("Received Question: %+v\n", question)

		// maybe go routines for adding the rows?
		// with mutex and all
		// add a question to the database
		err = db.Add(question)
		if err != nil {
			log.Printf("Error while saving to database: %s", err)
			return c.Status(fiber.StatusFailedDependency).SendString("Problems while saving to the database")
		} else {
			log.Println("The question has been successfully added to the database")
		}

		return c.Status(fiber.StatusAccepted).SendString("Trivia question has been successfully sent over!")
	})

	// retrieving values from
	host := viper.GetString("api_config.host")
	port := viper.GetInt("api_config.port")

	// create address and start the app
	address := fmt.Sprintf("%s:%d", host, port)
	err = app.Listen(address)
	if err != nil {
		log.Fatalf("Could not start the API: %v", err)
	}
}
