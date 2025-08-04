

let dashboardData = {};
let messageVolumeChart = null;
let successRateChart = null;

function initializeDashboard() {
    loadDashboardData();
    initializeCharts();
    setupEventListeners();
    startRealTimeUpdates();
}

function loadDashboardData() {
    frappe.call({
        method: 'flashchat_integration.utils.get_dashboard_data',
        callback: function(r) {
            if (r.message) {
                dashboardData = r.message;
                updateStatistics();
                updateRecentMessages();
                updateActiveCampaigns();
                updateCharts();
            }
        }
    });
}

function updateStatistics() {
    $('#total-messages').text(dashboardData.messages_this_week || 0);
    $('#delivered-messages').text(dashboardData.sms_sent + dashboardData.whatsapp_sent || 0);
    $('#pending-messages').text(dashboardData.pending_messages || 0);
    $('#failed-messages').text(dashboardData.failed_messages || 0);
}

function updateRecentMessages() {
    frappe.call({
        method: 'flashchat_integration.utils.get_recent_messages',
        args: { limit: 10 },
        callback: function(r) {
            if (r.message) {
                let tbody = $('#recent-messages-body');
                tbody.empty();
                
                r.message.forEach(function(msg) {
                    let statusClass = getStatusClass(msg.status);
                    let row = `
                        <tr>
                            <td>${formatDateTime(msg.sent_at)}</td>
                            <td>${msg.phone_number}</td>
                            <td><span class="badge badge-info">${msg.message_type}</span></td>
                            <td><span class="badge ${statusClass}">${msg.status}</span></td>
                            <td class="message-preview">${truncateMessage(msg.message_content)}</td>
                        </tr>
                    `;
                    tbody.append(row);
                });
            }
        }
    });
}

function updateActiveCampaigns() {
    frappe.call({
        method: 'flashchat_integration.utils.get_active_campaigns',
        callback: function(r) {
            if (r.message) {
                let container = $('#active-campaigns');
                container.empty();
                
                if (r.message.length === 0) {
                    container.html('<p class="text-muted">No active campaigns</p>');
                    return;
                }
                
                r.message.forEach(function(campaign) {
                    let progressPercent = campaign.total_recipients > 0 ? 
                        (campaign.messages_sent / campaign.total_recipients) * 100 : 0;
                    
                    let campaignCard = `
                        <div class="campaign-card mb-3">
                            <h6>${campaign.campaign_name}</h6>
                            <div class="progress mb-2">
                                <div class="progress-bar" style="width: ${progressPercent}%"></div>
                            </div>
                            <small class="text-muted">
                                ${campaign.messages_sent}/${campaign.total_recipients} sent
                            </small>
                        </div>
                    `;
                    container.append(campaignCard);
                });
            }
        }
    });
}

function initializeCharts() {
    // Message Volume Chart
    const ctx1 = document.getElementById('messageVolumeChart').getContext('2d');
    messageVolumeChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Messages Sent',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Success Rate Chart
    const ctx2 = document.getElementById('successRateChart').getContext('2d');
    successRateChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: ['Delivered', 'Failed', 'Pending'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgb(75, 192, 192)',
                    'rgb(255, 99, 132)',
                    'rgb(255, 205, 86)'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function updateCharts() {
    // Get chart data
    frappe.call({
        method: 'flashchat_integration.utils.get_chart_data',
        callback: function(r) {
            if (r.message) {
                // Update message volume chart
                messageVolumeChart.data.labels = r.message.volume_labels;
                messageVolumeChart.data.datasets[0].data = r.message.volume_data;
                messageVolumeChart.update();

                // Update success rate chart
                successRateChart.data.datasets[0].data = [
                    r.message.delivered_count,
                    r.message.failed_count,
                    r.message.pending_count
                ];
                successRateChart.update();
            }
        }
    });
}

function setupEventListeners() {
    // Message type change
    $('#messageType').change(function() {
        if ($(this).val() === 'OTP') {
            $('#messageGroup').hide();
        } else {
            $('#messageGroup').show();
        }
    });

    // Auto-refresh toggle
    $('#autoRefresh').change(function() {
        if ($(this).is(':checked')) {
            startRealTimeUpdates();
        } else {
            stopRealTimeUpdates();
        }
    });
}

let refreshInterval;

function startRealTimeUpdates() {
    refreshInterval = setInterval(function() {
        loadDashboardData();
    }, 30000); // Update every 30 seconds
}

function stopRealTimeUpdates() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Quick Actions
function sendQuickMessage() {
    $('#quickMessageModal').modal('show');
}

function createCampaign() {
    frappe.set_route('Form', 'FlashChat Campaign', 'new-flashchat-campaign-1');
}

function viewReports() {
    frappe.set_route('query-report', 'FlashChat Analytics');
}

function sendMessage() {
    let messageType = $('#messageType').val();
    let phoneNumber = $('#phoneNumber').val();
    let messageContent = $('#messageContent').val();

    if (!phoneNumber) {
        frappe.msgprint('Please enter a phone number');
        return;
    }

    if (messageType !== 'OTP' && !messageContent) {
        frappe.msgprint('Please enter a message');
        return;
    }

    let method = '';
    let args = { phone: phoneNumber };

    if (messageType === 'SMS') {
        method = 'flashchat_integration.api.send_sms_api';
        args.message = messageContent;
    } else if (messageType === 'WhatsApp') {
        method = 'flashchat_integration.api.send_whatsapp_api';
        args.message = messageContent;
        // Get WhatsApp account first
        frappe.call({
            method: 'flashchat_integration.api.get_whatsapp_accounts_api',
            callback: function(r) {
                if (r.message && r.message.success && r.message.accounts.length > 0) {
                    args.account = r.message.accounts[0].id;
                    args.recipient = phoneNumber;
                    sendMessageAPI(method, args);
                } else {
                    frappe.msgprint('No WhatsApp accounts available');
                }
            }
        });
        return;
    } else if (messageType === 'OTP') {
        method = 'flashchat_integration.api.send_otp_api';
        args.expire = 300;
    }

    sendMessageAPI(method, args);
}

function sendMessageAPI(method, args) {
    frappe.call({
        method: method,
        args: args,
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint('Message sent successfully!');
                $('#quickMessageModal').modal('hide');
                $('#quickMessageForm')[0].reset();
                loadDashboardData(); // Refresh data
            } else {
                frappe.msgprint('Failed to send message: ' + (r.message.error || 'Unknown error'));
            }
        }
    });
}

// Utility Functions
function getStatusClass(status) {
    switch (status) {
        case 'Delivered':
            return 'badge-success';
        case 'Failed':
            return 'badge-danger';
        case 'Sent':
            return 'badge-info';
        case 'Pending':
            return 'badge-warning';
        default:
            return 'badge-secondary';
    }
}

function formatDateTime(datetime) {
    if (!datetime) return '';
    return moment(datetime).format('MM/DD HH:mm');
}

function truncateMessage(message, length = 50) {
    if (!message) return '';
    return message.length > length ? message.substring(0, length) + '...' : message;
}

// Export functions for external use
window.flashchatDashboard = {
    loadDashboardData,
    sendQuickMessage,
    createCampaign,
    viewReports
};

