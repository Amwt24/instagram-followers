Instagram Follower Stats Scraper

🔍 Script to extract follower statistics from Instagram accounts using Selenium.

⚠️ Important Warnings

This script is for educational purposes only

Using bots for scraping violates Instagram’s Terms of Service

Your account may be blocked or banned for using this script

I am not responsible for how you use this code

🚀 Features

Extracts a list of followers from an account

Visits each follower’s profile

Retrieves each user’s follower count

Exports results in formatted CSV and TXT files

Complete logging system

Robust error handling

Screenshots for debugging

📋 Requirements

Python 3.8+

Google Chrome installed

Instagram account

🔧 Installation
1. Clone the repository
git clone https://github.com/Amwt24/instagram-followers.git
cd instagram-followers

2. Create a virtual environment (recommended)
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set up credentials
# Copy the example file
cp .env.example .env

# Edit .env with your credentials (use your favorite editor)
# NEVER upload this file to GitHub


Edit .env:

IG_USERNAME=your_username

IG_PASSWORD=your_password

💻 Usage
Basic configuration

Edit the variables in the main script:

count = 50  # Number of followers to analyze

account = "target_account"  # Target account

page = "followers"  # "followers" or "following"

Run the script

python instagram_follower_stats.py

📊 Results

The script generates 3 types of files:

1. CSV (account_followers_stats_TIMESTAMP.csv)
   
Username,Username_Follower,Num_Followers

target_account,follower1,1234

target_account,follower2,5678

2. Formatted TXT (account_followers_stats_TIMESTAMP.txt)

==================================

FOLLOWER ANALYSIS - target_account

Date: 2024-11-08 15:30:00

==================================

Username | Follower | Num Followers

-----------+-----------+----------------

target_account       | follower1                 |          1,234

target_account       | follower2                 |          5,678

3. Execution Log (logs/followers_stats_log_TIMESTAMP.txt)

Detailed record of all operations

Screenshots of each step

Error information for debugging

🔍 Debugging

If the script fails, check:

logs/ folder – contains screenshots of each step

.html file – page source at the time of the error

Log file – detailed process information

Useful files:

step1_homepage_*.png – Instagram homepage

step2_login_page_*.png – Login page

step3_credentials_entered_*.png – After entering credentials

step4_after_login_click_*.png – After login

⚙️ Advanced Configuration

Environment Variables

You can use environment variables instead of the .env file:

# Windows

set IG_USERNAME=your_username

set IG_PASSWORD=your_password

python instagram_follower_stats.py

# Linux/Mac

export IG_USERNAME=your_username

export IG_PASSWORD=your_password

python instagram_follower_stats.py

Modify Delays

To avoid detection, adjust the delays:

human_delay(2, 4)  # min_seconds, max_seconds

🛡️ Anti-Detection Measures

The script includes:

Random user agents

Random delays between actions

Character-by-character typing

Disabled automation indicators

Progressive scrolling

Still, Instagram may detect and block your account.

❗ Common Issues

"Login error"

Check your credentials in .env

Instagram may require verification

Your IP might be temporarily blocked

"Modal not found"

Instagram changed its HTML structure

Check the screenshots in logs/

The profile might be private

"Failed to fetch followers"

Private account

Nonexistent profile

Instagram blocked access

📝 Limitations

Does not work with private accounts (unless you follow them)

Rate limiting: Instagram restricts requests

Detection: Excessive use may result in a ban

HTML changes: Instagram frequently updates its structure

🤝 Contributions

Contributions are welcome:

Fork the project

Create a branch (git checkout -b feature/improvement)

Commit your changes (git commit -m 'Add improvement')

Push to the branch (git push origin feature/improvement)

Open a Pull Request

📜 License

This project is open-source under the MIT license.

⚖️ Legal Disclaimer

This software is provided “as is”, without any warranty of any kind. Use this script at your own risk. The authors are not responsible for:

Banned or blocked accounts

Data loss

Terms of service violations

Any direct or indirect damages

Use it at your own risk and responsibility.

📧 Contact

If you have questions or suggestions, open an issue on GitHub.

⭐ If you found this project useful, consider giving it a star on GitHub.
