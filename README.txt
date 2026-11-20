FOODSHARE - SIMPLE WINDOWS VERSION
==================================
Files: app.py, requirements.txt, START.bat
No templates folder and no static folder needed! CSS + HTML are inside app.py.

1. Install Python from python.org (choose Add Python to PATH).
2. Install MongoDB Community Server and ensure its service is running.
3. Extract ZIP, open the FoodShare_SIMPLE_Windows folder.
4. Double-click START.bat. Keep the black command window open.
5. Visit http://127.0.0.1:5000 in Chrome.

Alternative: in VS Code Terminal inside this folder:
  py -m pip install -r requirements.txt
  py app.py

If the browser says 'This site can't be reached', check that the terminal
shows 'Running on http://127.0.0.1:5000'. If not, read the error there.
If you see 'MongoDB connection error', start/install MongoDB Server.

Database: FoodShareDB
Collections: donors, receivers, food_listings, pickups.
Each collection supports Create / Read / Update / Delete in the browser.
Record IDs auto-created D1, R1, L1, P1, etc.
Relationships: use IDs such as D1 in food_listings.donorId;
L1 and R1 in pickups.listingId and pickups.receiverId.
This simplified classroom demo does not enforce foreign keys or automate pickups.
