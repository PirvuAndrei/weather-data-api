# Weather Data REST API

This Python application provides historical weather data from various stations across Europe. It is built using the Flask framework and offers a REST API for users to access weather information.

## Features

1. **Webpage Documentation:**
   - The app includes a main webpage in HTML that explains how it works.
   - Users can visit this page to understand the app's functionality and usage.
   - This page displays the names of available stations.

2. **Data Retrieval via URL:**
   - Users can search for weather data by station number using the app's URL.
   - If a user enters a specific station number, the REST API will return all available data (including temperature) for that station.

3. **Search by Year:**
   - Users can also search for weather data by specifying both the station number and a particular year.
   - The REST API will provide data for that station during the specified year.

4. **Specific Date Search:**
   - For more granular queries, users can search for a specific date along with the station number.
   - The REST API will return the temperature that particular day.

## Installation

1. Clone this repository to your local machine:
   ```
   git clone https://github.com/Mahdi-Meyghani/Historical-Weather-Data-API.git
   ```

2. Install the required dependencies using the `requirements.txt` file:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   python main.py
   ```

## Usage

1. Access the main webpage to learn about the app's features and how to use it.

2. To retrieve weather data:
   - Use the following URL format: `http://localhost:5000/api/v1/{station_number}/{date}` 
   - Or `http://localhost:5000/api/v1/yearly/{station_number}/{year}`
   - Or `http://localhost:5000/api/v1/{station_number}`
   - Replace `{station_number}`, `{year}`, and `{date}` with the desired values.
   - Example: `http://localhost:5000/api/v1/24/1874-10-08`

3. The API will return data in JSON format, including temperature and other relevant information.

## Contributing

Contributions are welcome! If you find any issues or have suggestions, feel free to create a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Remember to replace placeholders like `{station_number}`, `{year}`, and `{date}` with actual values relevant to your app. Happy coding! 🌦️🌡️🌤️
