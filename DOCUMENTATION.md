# Omada Controller View Documentation

## 1. Features

The Omada Controller View is a comprehensive web application designed to interface with the TP-Link Omada Controller, providing a user-friendly dashboard for network management and monitoring.

### Key Features:

*   **Secure Authentication**:
    *   Users can securely log in using their Omada Controller credentials (URL, Username, Password).
    *   Supports session management via access and refresh tokens.

*   **Multi-Site Management**:
    *   View and manage multiple sites configured in the Omada Controller.
    *   Easy switching between different sites from the sidebar.

*   **Interactive Dashboard**:
    *   **Site Overview**: Real-time statistics on Total/Connected Gateways, Switches, Access Points (APs), and Clients.
    *   **Visual Diagrams**: (If applicable) Network topology or status diagrams.

*   **Device Management**:
    *   **Device List**: Comprehensive list of all devices (APs, Switches, Gateways) with status indicators (Connected, Disconnected, Pending, etc.).
    *   **Detailed View**: Deep dive into specific device metrics including Model, MAC/IP Address, Uptime, CPU, and Memory usage.

*   **Traffic Monitoring**:
    *   **Real-time Charts**: Interactive line charts visualizing TX (Transmit) and RX (Receive) data over time.
    *   **Device Filtering**: Filter traffic data by specific Access Points or Switches.
    *   **Data Tables**: Tabular view of traffic activities for detailed analysis.

*   **Audit Logs**:
    *   **Site & Global Logs**: View historical events and system logs.
    *   **Filtering**: Filter logs by severity (Error, Warning, Info) to quickly identify issues.
    *   **Actions**: Options to resolve or remove log entries (UI placeholders for future implementation).

*   **AI Dashboard**:
    *   Leverages AI to provide insights and analytics on network performance (implementation details depend on the specific AI logic).

*   **AI Chatbot Assistant**:
    *   Integrated chatbot to answer user queries regarding the network or application usage.
    *   Uses RAG (Retrieval-Augmented Generation) to provide context-aware responses.

## 2. Instructions to Start the Project

This project consists of a Python Flask backend and a React frontend. Follow the steps below to set up and run the application.

### Prerequisites:
*   **Node.js** (v14 or higher) and **npm**
*   **Python** (v3.8 or higher)
*   **Firebase Credentials**: A `serviceAccountKey.json` file placed in the `backend/` directory for Firestore integration.

### Backend Setup:

1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```

2.  (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Start the Flask server:
    ```bash
    python main.py
    ```
    The backend server will start on `http://0.0.0.0:5000`.

### Frontend Setup:

1.  Open a new terminal and navigate to the frontend directory:
    ```bash
    cd frontend
    ```

2.  **Important Configuration**:
    *   Open `src/Login.js`.
    *   Locate the `NGROK_URL` constant.
    *   Update it to point to your running backend server (e.g., `http://localhost:5000` or your specific Ngrok URL).

3.  Install Node.js dependencies:
    ```bash
    npm install
    ```

4.  Start the React development server:
    ```bash
    npm start
    ```
    The application will open in your browser at `http://localhost:3000`.

## 3. Process and Workflow

### 1. Initialization
*   When the backend starts, it initializes the connection to Firebase Firestore using the provided credentials.
*   The frontend loads and presents the Login screen.

### 2. User Authentication
*   **Step 1**: User enters the Omada Controller Base URL, Username, and Password.
*   **Step 2**: The frontend sends these credentials to the backend (`/login`).
*   **Step 3**: The backend authenticates with the actual Omada Controller API and retrieves an `access_token`.
*   **Step 4**: On success, the user is redirected to the Dashboard.

### 3. Monitoring & Management
*   **Dashboard View**: Upon login, the user sees the Site Dashboard. They can select different sites from the sidebar.
*   **Navigation**: Users can navigate to "Devices", "Traffic", "Audit Log", or "AI Dashboard" using the sidebar menu.
*   **Data Fetching**:
    *   The frontend makes API calls to the Flask backend (e.g., `/sites/:id/devices`).
    *   The Flask backend acts as a proxy/middleware, forwarding requests to the Omada Controller API and processing the responses before sending them back to the frontend.
    *   Traffic data and logs may also be synced or retrieved from Firebase/Local Database depending on the specific implementation.

### 4. Troubleshooting & Assistance
*   Users can open the **Chatbot** from the bottom-right corner to ask questions.
*   The chatbot processes the message via the backend (`/chat`), which uses AI to generate a helpful response based on the network context.

## 4. Troubleshooting & Common Considerations

When running the project, you may encounter the following common issues. Here is how to resolve them:

### 1. Connection Refused / Failed to Fetch
*   **Symptom**: The frontend displays "Failed to fetch" or "Network Error" when trying to login.
*   **Cause**: The frontend cannot reach the backend server.
*   **Solution**:
    *   Ensure the Python backend is running (`python main.py`).
    *   Check the `NGROK_URL` in `frontend/src/Login.js`. If you are running locally, it should be `http://localhost:5000`. If using Ngrok, ensure the tunnel is active and the URL matches exactly.
    *   Check for Mixed Content errors in the browser console (e.g., trying to access http backend from https frontend).

### 2. Authentication Failed
*   **Symptom**: "Invalid credentials" error despite correct username/password.
*   **Cause**:
    *   The **Base URL** provided for the Omada Controller is incorrect or unreachable from the *backend* server.
    *   The Omada Controller is offline.
*   **Solution**:
    *   Verify the Base URL (e.g., `https://192.168.0.200:8043`).
    *   Ensure the backend server has network access to that IP/URL.

### 3. Firebase / Firestore Errors
*   **Symptom**: Backend crashes or errors related to "Certificate" or "Credentials".
*   **Cause**: The `serviceAccountKey.json` file is missing or invalid.
*   **Solution**:
    *   Ensure you have downloaded your Firebase Service Account key.
    *   Rename it to `serviceAccountKey.json`.
    *   Place it in the `backend/` directory.

### 4. SSL/TLS Certificate Warnings
*   **Symptom**: Backend logs show `SSLError` or `InsecureRequestWarning`.
*   **Cause**: Omada Controllers often use self-signed certificates.
*   **Solution**: The backend code is configured to ignore SSL verification (`verify=False`) for compatibility. Ensure this setting is maintained in `requests` calls if you modify the code.

### 5. Empty Charts or Data
*   **Symptom**: Traffic charts are empty or show no data.
*   **Cause**:
    *   No traffic data exists for the selected time range (default is usually the last hour).
    *   The Controller API response format might differ from what the backend expects.
*   **Solution**: Generate some network traffic on the devices and refresh. Check backend terminal logs for API response structures.

### 6. CORS Issues
*   **Symptom**: Browser console shows "Cross-Origin Request Blocked".
*   **Cause**: The backend is not allowing requests from the frontend's origin.
*   **Solution**: Ensure `CORS(app)` is enabled in `backend/main.py`. If using a specific domain, configure CORS to allow that origin.
