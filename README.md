# Indian Stock Price Dashboard

This easy-to-use dashboard is designed to help you track Indian stock prices and analyze your portfolio. 
It fetches stock data for the previous trading day (d-1) using the Google Finance API via Google Sheets and is built with **Streamlit** for a simple and interactive experience.

## 🌟 Features

- **Day-1 Stock Data**: Get stock prices from the previous trading day, ensuring reliable and consistent data.
- **Interactive Dashboard**: Navigate and analyze your portfolio with a clean and intuitive interface.
- **Portfolio Insights**: All your stock data in one place for better decision-making.
- **User-Friendly Design**: Built for anyone; no technical expertise is required.

## 🚀 Demo

Try out the live dashboard: [Indian Stock Price Dashboard](https://app-stock-portfolio.streamlit.app)

![Dashboard Preview]()  

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Source**: Google Sheets connected to Google Finance API
- **Hosting**: Streamlit Cloud

## 📈 How It Works

The dashboard retrieves stock data through Google Sheets, which fetches it from the **Google Finance API**. This setup ensures that the data is both accurate and easy to manage.

## 📋 Installation

Want to run the dashboard on your own machine? Here's how:

1. Clone this repository:
   ```bash
   git clone https://github.com/Mega-Barrel/streamlit-stock-portfolio.git
   cd indian-stock-dashboard
   ```

2. Set up a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open your browser and go to `http://localhost:8501` to see the dashboard in action.

## 📂 Project Layout

Here's an overview of the files:

```
indian-stock-dashboard/
├── app.py               # The main file that runs the dashboard
├── requirements.txt     # List of Python dependencies
├── data/                # Folder for storing any local data
├── utils.py             # Helper functions for data processing
└── README.md            # Documentation for the project
```

## 🛡️ License

This project is available under the [MIT License](LICENSE).

## 🤝 Contributing

Your ideas and improvements are welcome! To contribute:

1. Fork this repository
2. Create a new branch for your feature: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to your branch: `git push origin feature-name`
5. Open a pull request

## ✉️ Get in Touch

Have questions or feedback? Reach out to me:

- **Portfolio**: [Saurabh Joshi](https://mega-barrel.github.io)
- **LinkedIn**: [Connect with me](https://www.linkedin.com/in/saurabhJoshi2403)

---

⭐ If you enjoy this project, a star on GitHub would mean a lot!
