// Expects API_ENDPOINTS to be defined in config.js

function filterLogs() {
    const input = document.getElementById("logFilter").value.toLowerCase();
    const rows = document.querySelectorAll("#logTable tbody tr");
    rows.forEach(row => {
      const cells = Array.from(row.getElementsByTagName("td"));
      const match = cells.some(cell => cell.textContent.toLowerCase().includes(input));
      row.style.display = match ? "" : "none";
    });
  }
  
  function filterColumn(colIndex) {
    const inputs = document.querySelectorAll("th input");
    const rows = document.querySelectorAll("#logTable tbody tr");
    rows.forEach(row => {
      let showRow = true;
      const cells = row.getElementsByTagName("td");
      inputs.forEach((input, idx) => {
        const filterValue = input.value.toLowerCase();
        const cell = cells[idx];
        if (cell) {
          const cellValue = cell.textContent.toLowerCase();
          if (filterValue && !cellValue.includes(filterValue)) {
            showRow = false;
          }
        }
      });
      row.style.display = showRow ? "" : "none";
    });
  }
  
  function refreshPage() {
    location.reload();
  }
  
  // Loader functions: add and remove a loader overlay.
  function showLoader() {
    let loader = document.getElementById("loader");
    if (!loader) {
      loader = document.createElement("div");
      loader.id = "loader";
      // Basic styling for full-screen overlay; adjust as needed.
      loader.className = "fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-50 z-50";
      loader.innerHTML = `<div class="text-white text-xl">Loading...</div>`;
      document.body.appendChild(loader);
    }
  }
  
  function hideLoader() {
    const loader = document.getElementById("loader");
    if (loader) {
      loader.remove();
    }
  }
  
  // Main function to fetch logs.
  function fetchLogs() {
    let selectedDate = document.getElementById("logDate").value;
    const selectedCategory = document.getElementById("logCategory").value;
    
    if (!selectedDate) {
      // Use current Pakistan date
      selectedDate = setDate();
    }
    
    // Convert date from "YYYY-MM-DD" to "YYYYMMDD"
    const formattedDate = selectedDate.split("-").join("");
    
    // Determine the API endpoint based on the category.
    const selectedApi = API_ENDPOINTS[selectedCategory];
    if (!selectedApi) {
      alert("API endpoint for the selected category is not configured.");
      return;
    }
    
    // Append a cache-busting timestamp.
    const url = `${selectedApi}?date=${formattedDate}&_=${new Date().getTime()}`;
    
    // Disable the button to prevent rapid repeated clicks.
    const fetchButton = document.getElementById("fetchBtn");
    if (fetchButton) {
      fetchButton.disabled = true;
    }
    
    // Show loader overlay.
    showLoader();
    
    fetch(url, {
        method: "GET",
        cache: "no-store"
      })
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(data => {
        generateHeader(data.headers);
        generateRecords(data.headers, data.logs);
        setDate();
      })
      .catch(error => {
        console.error("Error fetching logs:", error);
        alert("Error fetching logs from the selected endpoint.");
      })
      .finally(() => {
        hideLoader();
        if (fetchButton) {
          fetchButton.disabled = false;
        }
      });
  }
  
  function generateHeader(headerList) {
    const table = document.getElementById("logTable");
    const tableHeader = table.getElementsByTagName("thead")[0];
    const tableHeaderRecord = tableHeader.getElementsByTagName("tr")[0];
    
    // Clear previous headers.
    tableHeaderRecord.innerHTML = "";
  
    headerList.forEach((headerText, index) => {
      const newHeaderCell = document.createElement("th");
      newHeaderCell.className = "py-3 px-4 border-b border-gray-600";
      newHeaderCell.textContent = headerText;
      
      // Add a line break.
      newHeaderCell.appendChild(document.createElement("br"));
      
      // Create a filter input field.
      const filterElement = document.createElement("input");
      filterElement.type = "text";
      filterElement.placeholder = "Filter...";
      filterElement.className = "mt-1 p-1 w-full bg-gray-900 text-gray-300 border border-gray-600 rounded";
      
      filterElement.onkeyup = () => filterColumn(index);
      
      newHeaderCell.appendChild(filterElement);
      tableHeaderRecord.appendChild(newHeaderCell);
    });
  }
  
  function generateRecords(headerList, logs) {
    const table = document.getElementById("logTable");
    const tableBody = table.getElementsByTagName("tbody")[0];
    
    tableBody.innerHTML = "";
    
    logs.forEach((log, index) => {
      const tableRecord = document.createElement("tr");
      tableRecord.className = (index % 2 === 0)
        ? "bg-gray-800 hover:bg-gray-700"
        : "bg-gray-900 hover:bg-gray-800";
        
      headerList.forEach(header => {
        const cell = document.createElement("td");
        cell.className = "py-2 px-4 border-b border-gray-700";
        
        let value = log[header] || "";
        if (typeof value === "object") {
          value = "<pre>" + JSON.stringify(value, null, 2) + "</pre>";
        }
        
        cell.innerHTML = value;
        tableRecord.appendChild(cell);
      });
      tableBody.appendChild(tableRecord);
    });
  }
  
  function setDate() {
    // Get the date in Pakistan Standard Time (GMT+5)
    const now = new Date();
    // Create date formatter for Pakistan time
    const options = { 
      timeZone: 'Asia/Karachi',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    };
    
    // Format the date in YYYY-MM-DD format for Pakistan timezone
    const formatter = new Intl.DateTimeFormat('en-CA', options); // en-CA gives YYYY-MM-DD format
    const pkDate = formatter.format(now);
    
    // Set the date display and input value
    const h1 = document.getElementById("log-heading");
    h1.innerHTML = `Logs for ${pkDate}`;
    document.getElementById("logDate").value = pkDate;
    
    console.log("Current date in Pakistan:", pkDate);
    return pkDate;
  }
  
  window.onload = function () {
    try {
      // Force using the current date and get Pakistan time
      const today = setDate();
      
      // Start real-time Pakistan clock
      updateRealTimeClock();
      
      // Get and parse the test log data
      let logDataElement = document.getElementById("logData").textContent;
      // Replace the placeholder with actual Pakistan date
      logDataElement = logDataElement.replace('"date": "CURRENT_DATE"', `"date": "${today}"`);
      
      const logData = JSON.parse(logDataElement);
      
      generateHeader(logData.headers);
      generateRecords(logData.headers, logData.logs);
    } catch (error) {
      console.error("Error parsing initial log data:", error);
      setDate();
    }
  };
  
  // Helper function to get Pakistan current date and time
  function getPakistanDateTime() {
    const now = new Date();
    const options = { 
      timeZone: 'Asia/Karachi',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    };
    
    return new Intl.DateTimeFormat('en-US', options).format(now);
  }

  // Update UI with real-time Pakistan time
  function updateRealTimeClock() {
    const timeElement = document.getElementById("pakistan-time");
    if (timeElement) {
      timeElement.textContent = getPakistanDateTime();
    }
    // Update every second
    setTimeout(updateRealTimeClock, 1000);
  }
  