# AI-enabled Customer Grievance Management / Smart Ticketing System

## My Recurring Task

### 1. Ticket Handling & Follow-up Process

#### 1. Customer Initiates the Request
The customer has a request, complaint, grievance or NRB-related grievance/query.

The customer contacts the Bank through one of the available channels:
- Email
- Telephone/Call
- Viber
- Social Media

**Output:** Customer request/grievance received by Customer Care.

#### 2. Customer Care Receives the Query
The request reaches the Customer Care function.

Currently, 25 outsourced agents are engaged to support the process on a 24/7 basis.

The agent receives and reviews the customer's communication.

#### 3. Manual Review of Customer Request
The Customer Care agent manually reads/listens to the request to understand:
- What the customer is requesting
- Nature of the complaint/grievance
- Which branch or unit should handle the issue

**Current dependency:** The initial understanding and identification of the responsible branch/unit require human intervention.

#### 4. Manual Identification of Concerned Branch/Unit
Based on the nature of the query, Customer Care manually identifies the branch/unit responsible for handling the issue.

Example:

Customer Request → Review → Identify Responsible Branch/Unit

#### 5. Manual Ticket Creation
After identifying the nature of the issue, the Customer Care staff manually creates a ticket in the existing ticketing system.

Relevant details of the query/grievance are entered into the system.

**Manual Activity:** Customer Care staff has to convert the incoming customer communication into a ticket.

#### 6. Unique Ticket ID Generation
Once the ticket is created successfully, the ticketing system generates a unique Ticket ID.

This Ticket ID becomes the reference for tracking the customer's request/grievance.

#### 7. Ticket Assignment
The Customer Care staff manually assigns the ticket to the concerned branch/unit staff.

**Current Assignment Model:**

Ticket → Concerned Individual Staff

This creates dependency on the staff to whom the ticket was originally assigned.

#### 8. Email Notification/Reminder
Once the ticket has been created and assigned, an email notification/reminder is sent to the respective staff.

The concerned branch/unit staff is informed that a ticket requires action.

#### 9. Branch/Unit Staff Reviews the Ticket
The assigned staff accesses/reviews the ticket.

The staff examines:
- Customer's request/grievance
- Information available in the ticket
- Action required from the branch/unit

#### 10. Branch/Unit Takes Necessary Action
The assigned staff takes the necessary action to address the customer request or grievance.

Where resolution depends on further investigation or action, the ticket remains pending until the required action is completed.

#### 11. TAT Tracking
A predefined Turnaround Time (TAT) is available in the system for resolution of the ticket.

The ticketing system is used to track the details/status of the customer issue.

#### 12. Follow-up on Pending Ticket
If the ticket remains unresolved, follow-up is required with the concerned branch/unit staff.

This creates ongoing follow-up activity for Customer Care, particularly for tickets approaching or exceeding their defined TAT.

#### 13. Staff Transfer Issue
A key issue occurs when the staff to whom the ticket was assigned is transferred.

**Current Situation:**
- Ticket assigned to Staff A
- Staff A transferred to another location/unit
- Existing ticket remains assigned to Staff A
- Ticket may not reach the appropriate current staff promptly
- Resolution may be delayed
- Customer suffers due to the delay

This is one of the main gaps in the existing assignment process.

#### 14. Resolution of Customer Issue
Once the concerned branch/unit completes the necessary action, the issue is resolved.

The ticket details/status are updated in the ticketing system.

#### 15. Ticket Closure
After resolution, the ticket is closed in the system.

The ticketing system retains the details of the query/issue for tracking/reference.

## Problems to Address

- Reduce the number of outsourced staff.
- Significant manual intervention in creating, categorizing, and assigning tickets.
- High turnover of outsourced staff and the need to train new staff.
- Tickets remain assigned to transferred staff, causing delays and customer dissatisfaction.

## Intended Users

- Customers
- Branch Staff
- Unit Staff

## Areas of Exploration

- AI-based automatic ticket creation from emails, calls, Viber, and social media.
- Intelligent ticket classification and routing.
- Role/branch-based assignment instead of individual-based assignment.
- Automated TAT monitoring and escalation.
- AI self-service for common customer queries.
- Centralized omnichannel case management.
- Automated acknowledgement and status updates.
- Management dashboards and analytics.
- Gradual reduction of dependency on outsourced agents.

## Tools

- Ticketing System
- Orbit 360 (all calls and emails are received through this platform before tickets are raised).

# AI Implementation Roadmap

## Phase 1: Assess Current Process
- Review the existing Orbit 360 → Ticketing System process.
- Analyze ticket volumes, categories, TAT, and manual activities.
- Identify repetitive work handled by outsourced agents.

**Output:** Identify what can be automated.

## Phase 2: Prepare Process & Data
- Standardize grievance categories and TAT.
- Develop branch/unit routing rules.
- Shift from individual-based to queue-based assignment.
- Prepare an approved knowledge base.

**Output:** AI-ready process.

## Phase 3: Pilot AI
Start with email.

AI suggests:
- Type of grievance
- Category
- Priority
- Responsible branch/unit

Human validates recommendations.

**Output:** Test AI accuracy while retaining human control.

## Phase 4: Automate Ticket Creation & Routing
Customer Request
→ AI Reads & Classifies
→ Ticket Automatically Created
→ Unique Ticket ID
→ Customer Acknowledgement
→ Automatically Routed to Branch/Unit Queue

**Output:** Reduced manual ticket creation and assignment.

## Phase 5: Automate TAT & Follow-up
Ticket Created
→ TAT Starts
→ Automatic Monitoring
→ Reminder Before Due Date
→ Escalation if Overdue
→ Human Action

**Output:** Reduced manual follow-up and TAT breaches.

## Phase 6: AI + Human Resolution
### AI
- Summarizes cases
- Finds relevant approved knowledge
- Supports staff with information
- Drafts customer responses

### Human
- Investigates
- Makes decisions
- Approves sensitive cases
- Resolves grievances

**Output:** Faster handling while retaining human oversight.

## Phase 7: Scale & Optimize
- Expand to additional channels.
- Introduce customer self-service.
- Build management dashboards.
- Measure AI accuracy, TAT, and workload.
- Review manpower requirements.
- Optimize outsourced staffing based on evidence.

**Output:** Lower manual workload, better customer service, and optimized manpower.

# Roadmap at a Glance

1. Assess Current Process
2. Prepare Data, Knowledge & Routing Rules
3. Pilot AI on Email
4. Automate Ticket Creation & Smart Routing
5. Automate TAT, Reminder & Escalation
6. AI-Assisted + Human Resolution
7. Scale, Measure & Optimize Manpower
