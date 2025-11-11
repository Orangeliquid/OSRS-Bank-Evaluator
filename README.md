# Old School Runescape Bank Evaluator
The OSRS Bank Evaluator allows you to import your bank items into a SQLite database with the press of a button! The web application is displayed via StreamLit and offers three tabs for bank evaluation and analysis. The 'View Bank Snapshots' tab allows you to import, view (via dataframe), and delete your bank snapshots. 'Compare Item Prices' offers the option to fetch and enter current item prices for your selected bank and query price snapshots for items via a search box. Finally, the 'Compare Snapshots' tab beckons you to select two banks from your database to compare and contrast the following metrics: Item quantity, Item prices, Top priced items, Top quantity items, and Bank value.

## Table of Contents
- [Installation](#installation)
- [Getting-Started](#getting-started)
- [Screenshots](#screenshots)
  - [View-Bank-Snapshots](#view-bank-snapshots)
  - [Compare-Item-Prices](#compare-item-prices)
  - [Compare-Snapshots](#compare-snapshots)
- [License](#license)

## Installation

To run Mass Shooting Visualizer, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Orangeliquid/OSRS-Bank-Evaluator
   cd OSRS-Bank-Evaluator
   ```

2. Ensure UV is downloaded:
   - If UV is not downloaded on your system, download it via pip:
   ```bash
   pip install uv
   ```

3. Sync dependencies with UV:
   ```bash
   uv sync
   ```

## Getting Started

1. Verify your current directory in your terminal is in OSRS-Bank-Evaluator
   - in terminal run:
      ```bash
      uv run streamlit run streamlit_app.py
      ```

2. Your web browser will now open up and the web application will be displaying the 'View Bank Snapshots' tab
   - Click the 'Import New Bank' expander
   - Follow the instructions
   - In the 'Bank Name' Field type in your desired name for the bank snapshot
   - Press 'Submit Bank Data'
   - Verify 'Total items' is accurate with the total items in your OSRS Bank
   - If correct, select 'Bank item count is CORRECT'
   - If incorrect, select 'INCORRECT bank item count' and try to copy the bank tsv from the runelite plugin once more

3. A Bank snapshot is now entered into the database, feel free to enter another snapshot if you have one or explore the other options:
   - The 'Show All Bank Items' checkbox will display the following information in a Pandas Dataframe for your selected bank:
     - name
     - quantity
     - is_tradeable
     - uncharged_id
     - has_ornament_kit_equipped
     - item_id

   - GP Valuation under the dataframe includes the following valuations:
     - Low estimate
     - Mean estimate
     - High estimate

   - You may also delete any current snapshots by selecting that snapshot and pressing "Submit deletion of 'selected_snapshot'" button

4. Navigate to the 'Compare Item Prices' tab
   - Select your prefered bank
   - Now use 'Search an item' text box to look up any item in your selected bank
   - If you aren't sure the exact name, type in a partial name to display similar named items('Dragon' brings up 10 similar items with 'Dragon' in the name).
   - When the exact name of an item is entered into the search box, a dataframe will be displayed summarizing the following:
     - item_name
     - quantity
     - single_item_price
     - low_value_estimate
     - mean_value_estimate
     - high_value_estimate
     - timestamp(when the prices were fetched and entered into db)
       
   - If a partial name of an item is searched, if possible, up to ten similar named items will be shown as expanders
   - For instance, "Dragon" is submitted and the following expanders populate:
     - Dragon boots
     - Dragon defender
     - Dragon Warhammer
     - Dragonfire shield
     - Dragon hunter lance
     - Dragon hunter crossbow(b)
     - Snapdragon seed
     - Dragonstone bolts
     - Dragonstone bolts(e)
     - Ruby dragon bolts(e)
       
   - Each of these expanders may be clicked to display the same info discussed above when typing in an exact name
   - Untradeable or items deemed to have no value will simply say "'item' is untradeble!"
   - Notice there is only one entry in the dataframe when looking at an item, this is what was submitted when you imported your bank snapshot.
   - To get more valuation entries for each item, press the 'Get Current Prices' for any snapshot you wish to update.
   - By default, there is a 12 hour cooldown to fetch current prices, to change this cooldown do the following:
     - Navigate to app/utils/snapshot.py
     - Locate line 12 -> COOLDOWN = timedelta(hours=12) -> change 12 to 0
     - rerun the application
   - This cooldown is implemented to prevent spamming of current prices which will always enter an entry for the item into the db
   - I advise you to always select 'Get Current Prices' for all banks(go through each bank in the dropdown and click the Get Current Prices button) after the cooldown for trend analysis.

5. Navigate to 'Compare Snapshots'
   - If you have only imported 1 snapshot, this tab will not allow you to use it seeing as this is to compare the data between two banks
   - With at least 2 banks you will be able to select each bank, one on the left, one on the right
   - Two dataframes will auto populate for each bank, displaying 'name' and 'quantity' of items in each bank
   - The checkboxes under 'Data Frame Filters' allow you to add more information for comparison:
     - is_tradeable
     - uncharged_id
     - has_ornament_kit_equipped
     - item_id

   - These filters are turned off by default because it makes the dataframes(which are already cramped) wider and requires scrolling to see the filters. Use them if you desire.
   - The GP Valuations expander under the dataframes display the following for each bank
     - Low Valuation
     - Mean Valuation
     - High Valuation
   
   - The Comparisons expander allows the user to select their desired form of Valuation Option, the same as mentioned under GP Valuations
   - The default option is 'mean_value'
   - A merged dataframe is displayed with the following data based on the Valuation Option selected:
     - name
     - quantity_Bank1
     - valuation_option_Bank1(example: mean_value_Bank1)
     - quantity_Bank2
     - valuation_option_Bank2(example: mean_value_Bank2)
     - quantity_diff(absolute value of quantity_Bank1 - quantity_Bank2)
     - mean_value_diff(absolute value of valuation_option_Bank1 - valuation_option_Bank2)
     - quantity_direction
       - 'Bank x is higher' if one bank has a higher quanity of this item than the other 
       - 'No Difference' if quantity of item is the same for both banks
       - 'Bank x missing' if said bank does not possess the item but the other bank does
   
   - The 'Top 10 Highest Value by Mean' section will display a dataframe for each bank selected with the following data:
     - name
     - quantity
     - mean_value

   - The 'Top 10 Highest Quantity of Items' section will display a dataframe for each bank selected with the following data:
     - name
     - quantity
     - mean_value

## Screenshots

### View Bank Snapshots

Initial run of web application will prompt you to 'Import New Bank'
<img width="881" height="560" alt="Start_View_Bank_Snapshots" src="https://github.com/user-attachments/assets/bd692031-1ca8-4c98-be19-8c484808e8c0" />

Follow the prompt to import your first bank
<img width="884" height="677" alt="VBS_2" src="https://github.com/user-attachments/assets/44bc747c-41ae-45ff-9dad-77f997ccbec1" />

Enter the name of your first bank
<img width="779" height="545" alt="VBS_3" src="https://github.com/user-attachments/assets/bd1abf46-7baa-469e-9b32-41ff0c6c99a0" />

Verify Total items count is correct with the total count in your bank
<img width="788" height="496" alt="VBS_4" src="https://github.com/user-attachments/assets/8d0de090-37c7-4509-9c0f-6ba0a73845e5" />

View all items in bank by pressing "Show All Bank Items" checkbox
<img width="787" height="813" alt="VBS_5" src="https://github.com/user-attachments/assets/3dc3f896-1023-4ab6-bc80-9ad13067b23a" />

Select bank and submit for deletion
<img width="871" height="770" alt="VBS_6" src="https://github.com/user-attachments/assets/1576e1e0-3c2d-456c-aca8-c1e64ecf6307" />

### Compare Item Prices
Initial run of web application will prompt you to navigate to 'View Bank Snapshots' and select 'Import New Bank'
<img width="886" height="467" alt="Start_Compare_Item_Prices" src="https://github.com/user-attachments/assets/a0787573-549d-45b7-ad5a-69921d1bf116" />

Error Message notifiy user they have already fetched current prices for this bank(Initial Bank Import counts) when pressing 'Get Current Prices' button
<img width="875" height="694" alt="CIP_2" src="https://github.com/user-attachments/assets/c4df74a7-aa67-491c-9c77-5e397e1d49b4" />

'Dragon' has been searched and 10 items in bank similar to entry are displayed with expanders containing each items pricing entries
<img width="785" height="858" alt="CIP_3" src="https://github.com/user-attachments/assets/459dd269-2763-42e3-bf5b-3767f60d9528" />

'Dragon Boots' are selected and a message reads the item is untradeable, 'Dragon Warhammer' is selected and tradeable, showing pricing data entry
<img width="807" height="560" alt="CIP_4" src="https://github.com/user-attachments/assets/e1fdff9b-4ae8-4e94-b535-dcb77be9b39f" />

'Eye of ayak' is entered and the exact item pricing data is shown in a dataframe
<img width="847" height="700" alt="CIP_5" src="https://github.com/user-attachments/assets/72386e67-f89b-4f04-af55-f8e0bd079e05" />

### Compare Snapshots

Initial run of web application will prompt you to navigate to 'View Bank Snapshots' and select 'Import New Bank'
<img width="888" height="505" alt="Start_Compare_Snapshots" src="https://github.com/user-attachments/assets/e011a284-6102-417d-aa3b-922ebb8d48c4" />

If only one bank snapshot is imported, this error message will notifiy you that at least two snapshots must be imported to use this comparison tab
<img width="870" height="498" alt="CS_one_snapshot_only" src="https://github.com/user-attachments/assets/29aab91c-2040-4e88-9c2c-b932e2b976fd" />

Two banks are selected and none of the 'Data Frame Filters' are selected
<img width="814" height="473" alt="CS_3" src="https://github.com/user-attachments/assets/3018e756-8937-4ede-8e73-73dc7d427eae" />

Each of the selected banks and their Bank dataframes for comparison
<img width="816" height="476" alt="CS_4" src="https://github.com/user-attachments/assets/d7f3fa69-89d4-40c2-bcdd-39942e3b2129" />

'GP Valuations' expander is selected detailing each banks valuations
<img width="803" height="234" alt="CS_5" src="https://github.com/user-attachments/assets/3332bef4-f864-48df-8d77-f79228006fd5" />

'Comparisons' expander is selected and 'mean_value' is chosen for comparison in the merged dataframe below
<img width="757" height="569" alt="CS_6" src="https://github.com/user-attachments/assets/b9509493-8804-4ea1-86cb-c982e9379ed8" />

'Comparisons' expander is slid over to show other values in merged dataframe
<img width="749" height="565" alt="CS_7" src="https://github.com/user-attachments/assets/d0916ad3-c622-4639-a064-ae2e56123b9d" />

Top 10 Highest Value by Mean dataframe is show for bank 'Shadow'
<img width="752" height="505" alt="CS_8" src="https://github.com/user-attachments/assets/b49a8026-dd22-4f48-8cde-9b8fe9a5e49a" />

Top 10 Highest Value by Mean dataframe is show for bank 'No Shadow'
<img width="756" height="459" alt="CS_9" src="https://github.com/user-attachments/assets/7cc1f1a4-b6d8-4c8a-bb41-210f62bf0a9a" />

Top 10 Highest Quantity of Items dataframe is show for bank 'Shadow'
<img width="786" height="508" alt="CS_10" src="https://github.com/user-attachments/assets/39db1f79-0918-438c-b006-883b4cdd8030" />

Top 10 Highest Quantity of Items dataframe is show for bank 'No Shadow'
<img width="765" height="477" alt="CS_11" src="https://github.com/user-attachments/assets/8f22da41-5cbd-4a75-89b0-1919ce59f2f2" />


## License


