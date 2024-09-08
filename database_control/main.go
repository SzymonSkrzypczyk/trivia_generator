package main

import (
	"fmt"
	"log"

	"github.com/gofiber/fiber/v2"
	"github.com/spf13/viper"
)

type Question struct {
	Question       string `json:"question"`
	Answer_a       string `json:"answer_a"`
	Answer_b       string `json:"answer_b"`
	Answer_c       string `json:"answer_c"`
	Answer_d       string `json:"answer_d"`
	Correct_answer string `json:"correct_answer"`
}

func main() {
	// config loading
	viper.SetConfigFile("database_api_config.yaml")
	viper.SetConfigType("yaml")

	// load in config values
	err := viper.ReadInConfig()
	if err != nil {
		log.Fatalf("Error reading config file: %v", err)
	}

	// set defaults
	viper.SetDefault("api_config.host", "127.0.0.1")
	viper.SetDefault("api_config.port", 6000)

	// start fiber app
	app := fiber.New()

	// add an endpoint
	app.Post("/database", func(c *fiber.Ctx) error {
		var q Question

		if err := c.BodyParser(&q); err != nil {
			return c.Status(fiber.StatusBadRequest).SendString("Invalid JSON")
		}

		fmt.Printf("Received Question: %+v\n", q)

		return c.Status(fiber.StatusAccepted).SendString("Trivia question has been successfully sent over!")
	})

	// retrieving values from
	host := viper.GetString("api_config.host")
	port := viper.GetInt("api_config.port")

	// create address and start the app
	address := fmt.Sprintf("%s:%d", host, port)
	fmt.Println(address)
	//app.Listen(address)
}
