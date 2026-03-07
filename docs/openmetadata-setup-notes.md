# OpenMetadata: Aiera REST API Setup Notes

## What is OpenMetadata?

OpenMetadata (OMD) is a metadata platform for data discovery, governance, and observability. Think of it as a **catalog** — it doesn't store your actual data or run your APIs. Instead, it stores *metadata about* your data assets so people across the org can discover, understand, and trust them.

When we register the Aiera REST API in OMD, we're telling the platform: "Here's an API we run, here are its endpoints, and here's what the request/response shapes look like." This makes the API discoverable and documentable alongside all our other data assets (databases, dashboards, pipelines, etc.).

---

## What Does the REST Connector Do?

The REST connector is an **ingestion connector** (currently in BETA) that reads an OpenAPI spec and imports metadata about the API into OpenMetadata. Specifically, it ingests three things:

| What it ingests       | What that means                                                                                     |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| **API Endpoints**     | Each path in the spec (e.g. `/events`, `/calendar`, `/equities-v2`) becomes a cataloged endpoint    |
| **Request Schemas**   | The expected query parameters, path parameters, and request bodies for each endpoint                |
| **Response Schemas**  | The shape of data each endpoint returns                                                             |

After ingestion, anyone browsing OMD can see what endpoints the Aiera API exposes, what parameters they accept, and what they return — without needing to read raw YAML files or ask the API team.

---

## What Do We Need?

### 1. An OpenAPI Spec URL

The connector needs a **URL** pointing to an OpenAPI spec document. It does NOT read local files — it fetches the spec over HTTP(S).

**Our spec:** This repo contains the spec at `specs/unified.yaml`. It's an OpenAPI 3.1.0 document with ~2,480 lines covering 27 endpoints across these domains:

- Equities (`/equities-v2`, `/equities-v2/{equity_id}`, `/equities-v2/sectors`)
- Topics (`/topics`, `/topics/{topic_id}`, `/topics/from_equities`, `/topics/from_events`, etc.)
- Corporate Activity (`/corporate-activity`, `/corporate-activity/coverage`, etc.)
- Content (`/content/filings`, `/content/news`)
- Calendar (`/calendar`, `/calendar/coverage`, `/calendar/{event_id}`)
- Events (`/events`, `/events/{event_id}`, `/events/audio/transcript/csv`)
- Monitor (`/dashboards/{dashboard_guid}/streams/{stream_guid}/matches`)
- Speakers (`/events-v2/person/{person_id}`)
- Summaries (`/summaries`, `/summaries/{event_id}`, `/summaries/{event_id}/{summary_type}`)

**The hosting question:** The spec needs to be accessible at a URL that the OMD instance can reach. Options:

| Option                              | Pros                          | Cons                                     |
|-------------------------------------|-------------------------------|------------------------------------------|
| Raw GitHub URL (if repo is private, use a token) | Simple, version-controlled | GitHub raw URLs can be rate-limited       |
| Host on an internal server/S3       | Full control, no rate limits  | Need to set up hosting and keep it updated |
| Serve from the API itself (e.g. `/openapi.json`) | Self-documenting, always current | Requires API changes                     |

**Format note:** The OMD docs show a JSON example (`openapi.json`), but the connector should accept YAML as well since it's a standard OpenAPI format. If you run into issues, convert to JSON:
```bash
# Using yq (install via brew install yq)
yq -o=json specs/unified.yaml > specs/unified.json

# Or using Python
python -c "import yaml, json, sys; json.dump(yaml.safe_load(open('specs/unified.yaml')), sys.stdout, indent=2)" > specs/unified.json
```

### 2. Authentication Token (Optional)

This is **not** your Aiera API key. This is only needed if the URL where the spec is hosted requires authentication to access (e.g., a private GitHub raw URL). If the spec is publicly accessible or on an internal network the OMD instance can reach, you can leave this blank.

**For private GitHub repos:** You'll need a GitHub personal access token (PAT) since the OMD instance can't access raw file URLs without authentication. The raw URL format is:

```text
https://raw.githubusercontent.com/aiera-inc/aiera-rest-openapi/main/specs/unified.yaml
```

Two PAT options:

| Type                                | Scope                              | Notes                                             |
| ----------------------------------- | ---------------------------------- | ------------------------------------------------- |
| **Fine-grained PAT** (recommended)  | `Contents: Read` on this repo only | More secure, least-privilege                      |
| **Classic PAT**                     | `repo`                             | Broader access than needed, but simpler to set up |

Paste the PAT into the **Token** field in the OMD connector configuration. OMD sends it as a bearer token when fetching the spec.

Don't confuse this with:
- **Aiera API key** — used by consumers calling the actual API
- **OMD auth** — your login to the OpenMetadata platform itself

---

## Step-by-Step Setup in OpenMetadata

### Step 1: Prepare the Spec URL

Make `specs/unified.yaml` (or a JSON version) accessible at a URL. Verify it works:
```bash
curl -s <YOUR_SPEC_URL> | head -5
# Should show the openapi: 3.1.0 header
```

### Step 2: Create the Service in OMD

1. Log into your OpenMetadata instance
2. Go to **Settings > Services** (left sidebar)
3. Click **APIs** in the service category list
4. Click **Add New Service**

### Step 3: Select the Connector

1. Choose **REST** as the service type
2. Give it a name like `aiera-rest-api` (this is permanent and cannot be changed later)
3. Optionally add a description: "Aiera's financial data REST API"

### Step 4: Configure the Connection

1. **OpenAPI Schema URL**: Paste the URL to your hosted spec
2. **Token**: Leave blank unless the spec URL requires auth
3. Click **Test Connection** — this verifies OMD can fetch and parse the spec

### Step 5: Set Up Ingestion

1. Choose a schedule for how often OMD re-reads the spec:
   - **Daily** is a good default — specs don't change that often
   - **Manual** if you only want to run it on-demand
2. All times are in UTC
3. Click **Deploy** to create and start the ingestion pipeline

### Step 6: Verify

1. Go to **Explore > APIs** in the OMD UI
2. You should see your `aiera-rest-api` service with all 27 endpoints listed
3. Click into any endpoint to see its parameters and response schemas

---

## What to Expect After Setup

Once ingestion runs, you'll see in OMD:

- **An API Service** named whatever you called it (e.g., `aiera-rest-api`)
- **API Collections** grouping the endpoints (based on how OMD parses the spec's tags/paths)
- **API Endpoints** — one per path in the spec, each showing:
  - HTTP method (GET, POST, etc.)
  - Path parameters and query parameters
  - Request body schema (if applicable)
  - Response schema
- You can then add **descriptions**, **tags**, **owners**, and **tier classifications** to each endpoint within OMD to enrich the metadata beyond what the spec provides

### What it does NOT do

- It does not call or test the actual Aiera API
- It does not import actual data/responses
- It does not monitor API health or uptime
- It does not handle API authentication for consumers

---

## Potential Gotchas

1. **BETA status** — The REST connector is still in beta. Expect rough edges, especially around how it handles complex OpenAPI features (polymorphism, oneOf, etc.)

2. ~~**Spec title mismatch**~~ — **Resolved.** The spec title was updated from `Aiera Calendars API` to `Aiera REST API`.

3. **OpenAPI 3.1.0 compatibility** — The spec uses OpenAPI 3.1.0. If the OMD connector has issues parsing it, you may need to downgrade to 3.0.3 (the differences are minor but some parsers are picky).

4. **Network access** — The OMD instance must be able to reach the spec URL. If OMD is running in a private network, the spec needs to be hosted somewhere within that network.

5. **Schema completeness** — The quality of what shows up in OMD depends entirely on how detailed the OpenAPI spec is. If endpoints are missing response schemas or descriptions, those will be empty in OMD too.

---

## Glossary

| Term                  | Meaning                                                                                  |
|-----------------------|------------------------------------------------------------------------------------------|
| **OpenMetadata (OMD)**| The metadata platform we're setting up                                                   |
| **Connector**         | A plugin that knows how to pull metadata from a specific type of source                  |
| **Ingestion**         | The process of the connector reading metadata from a source and loading it into OMD      |
| **Service**           | A registered data source in OMD (our REST API will be one service)                       |
| **OpenAPI Spec**      | A standard format (YAML/JSON) for describing REST APIs — this is what we're feeding OMD  |
| **API Collection**    | A grouping of related endpoints within a service in OMD                                  |
| **API Endpoint**      | A single path+method combination (e.g., `GET /events`)                                   |

---

## References

- [OpenMetadata REST Connector Docs (v1.12.x)](https://docs.open-metadata.org/v1.12.x/connectors/api/rest)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- This repo's spec: `specs/unified.yaml`
