package main

import (
	"fmt"
	"log"

	"database_control/db_connector"

	"github.com/gofiber/fiber/v2"
	"github.com/spf13/viper"
)

func main() {
	// config loading
	viper.SetConfigFile("database_api_config.yaml")
	viper.SetConfigType("yaml")

	// load in config values
	err := viper.ReadInConfig()
	if err != nil {
		log.Fatalf("Error reading config file: %v", err)
	}

	// set defaults for API
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

	// start fiber app
	app := fiber.New()

	// open database connection
	db := db_connector.NewDB(
		viper.GetString("database.database_name"),
		viper.GetString("database.host"),
		viper.GetString("database.user"),
		viper.GetString("database.password"),
		viper.GetInt("database.port"),
		viper.GetBool("database.sslmode"))

	db.Open()

	// add an endpoint
	app.Post("/database", func(c *fiber.Ctx) error {
		var question db_connector.Question

		// retrieve
		if err := c.BodyParser(&question); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid JSON")
		}
		// will be logged!
		fmt.Printf("Received Question: %+v\n", question)

		// maybe go routines for adding the rows?
		// with mutex and all
		// add a question to the database
		db.Add(question)

		return c.Status(fiber.StatusAccepted).SendString("Trivia question has been successfully sent over!")
	})

	// retrieving values from
	host := viper.GetString("api_config.host")
	port := viper.GetInt("api_config.port")

	// create address and start the app
	address := fmt.Sprintf("%s:%d", host, port)
	app.Listen(address)
}
