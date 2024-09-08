package db_connector

import (
	"fmt"
	"log"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type Question struct {
	Id             int    `gorm:"primaryKey"`
	Question       string `json:"question"`
	Answer_a       string `gorm:"type:varchar(255)" json:"answer_a"`
	Answer_b       string `gorm:"type:varchar(255)" json:"answer_b"`
	Answer_c       string `gorm:"type:varchar(255)" json:"answer_c"`
	Answer_d       string `gorm:"type:varchar(255)" json:"answer_d"`
	Correct_answer string `gorm:"type:varchar(255)" json:"correct_answer"`
}

type DB struct {
	DatabaseName string
	Host         string
	Port         int
	User         string
	Password     string
	Sslmode      bool
	Conn         *gorm.DB
}

func (db DB) getURL() string {
	var disable string
	if !db.Sslmode {
		disable = "disable"
	} else {
		disable = "enable"
	}

	return fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=%s", db.Host, db.User,
		db.Password, db.DatabaseName, db.Port, disable)
}

func (db *DB) Open() error {
	database, err := gorm.Open(postgres.Open(db.getURL()), &gorm.Config{})
	if err != nil {
		log.Fatal(fmt.Errorf("failed to connect to the database: %w", err))
		return err
	}

	// add database to the DataBase structure
	db.Conn = database
	// auto migration
	db.Conn.AutoMigrate(&Question{})

	return nil
}

// maybe Generics here?
func (db DB) Add(question Question) error {
	// add a question to the database
	res := db.Conn.Create(&question)
	// check if the operation was successful
	if err := res.Error; err != nil {
		log.Printf("Error while adding to a database: %v", err)
		return res.Error
	}
	// if it was return nil error
	return nil
}

func (db DB) AddMany(questions []Question) error {
	// add a slice of Questions
	res := db.Conn.Create(&questions)

	// error validations
	if err := res.Error; err != nil {
		return err
	}

	return nil
}

func (db DB) GetMany(count int) ([]Question, error) {
	var questions []Question
	// check if the given count is correct
	if count <= 0 {
		log.Printf("The given count could not be accepted: %v", count)
		return questions, fmt.Errorf("you have to provide a correct count of rows to be returned")
	}
	// retrieve a given number of rows
	result := db.Conn.Limit(count).Find(&questions)

	// check if retrieving the rows was successful
	if err := result.Error; err != nil {
		log.Printf("Error while retrieving many: %v", err)
		return nil, result.Error
	}

	return questions, nil

}

func (db DB) GetSingle() (Question, error) {
	var res_question Question

	// retrieve the first element
	result := db.Conn.First(&res_question)

	if err := result.Error; err != nil {
		log.Printf("Error while retrieving single: %v", err)
		return res_question, fmt.Errorf("there was an error while retrieving the first row: %w", err)
	}

	return res_question, nil
}

func (db DB) GetRandom() (Question, error) {
	var res_question Question

	// retrieve a random row
	result := db.Conn.Order("RANDOM()").First(&res_question)

	// check if there is an error
	if err := result.Error; err != nil {
		log.Printf("Error while retrieving random: %v", err)
		return res_question, fmt.Errorf("there was an error while retrieving a random row: %w", err)
	}

	// if there are no errors
	return res_question, nil
}

func NewDB(databaseName, host, user, password string, port int, sslmode bool) *DB {
	return &DB{
		DatabaseName: databaseName,
		Host:         host,
		Port:         port,
		User:         user,
		Password:     password,
		Sslmode:      sslmode,
	}
}
