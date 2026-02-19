# OParl 1.1 Mapping - aitema|RIS

Mapping der OParl 1.1 Spezifikation auf die aitema|RIS Datenbank-Models.

## Objekt-Typen

| # | OParl-Typ | DB-Tabelle | SQLAlchemy Model | API-Endpoint |
|---|-----------|------------|------------------|--------------|
| 1 | `oparl:System` | `system` | `System` | `GET /api/v1/oparl/system` |
| 2 | `oparl:Body` | `body` | `Body` | `GET /api/v1/oparl/body` |
| 3 | `oparl:LegislativeTerm` | `legislative_term` | `LegislativeTerm` | `GET /api/v1/oparl/body/{id}/legislative-term` |
| 4 | `oparl:Organization` | `organization` | `Organization` | `GET /api/v1/oparl/body/{id}/organization` |
| 5 | `oparl:Person` | `person` | `Person` | `GET /api/v1/oparl/body/{id}/person` |
| 6 | `oparl:Membership` | `membership` | `Membership` | `GET /api/v1/oparl/organization/{id}/membership` |
| 7 | `oparl:Meeting` | `meeting` | `Meeting` | `GET /api/v1/oparl/body/{id}/meeting` |
| 8 | `oparl:AgendaItem` | `agenda_item` | `AgendaItem` | `GET /api/v1/oparl/meeting/{id}/agenda-item` |
| 9 | `oparl:Paper` | `paper` | `Paper` | `GET /api/v1/oparl/body/{id}/paper` |
| 10 | `oparl:Consultation` | `consultation` | `Consultation` | `GET /api/v1/oparl/paper/{id}/consultation` |
| 11 | `oparl:File` | `file` | `File` | `GET /api/v1/oparl/file/{id}` |
| 12 | `oparl:Location` | `location` | `Location` | `GET /api/v1/oparl/location/{id}` |

## Gemeinsame Eigenschaften (OParlMixin)

Alle OParl-Objekte erben folgende Felder:

| OParl-Eigenschaft | DB-Spalte | Typ | Pflicht |
|-------------------|-----------|-----|---------|
| `id` | `id` | UUID (als URL serialisiert) | Ja |
| `type` | `oparl_type` | String | Ja |
| `created` | `created` | DateTime (TZ) | Ja (auto) |
| `modified` | `modified` | DateTime (TZ) | Ja (auto) |
| `deleted` | `deleted` | Boolean | Ja (default: false) |
| `keyword` | `keyword` | String[] | Nein |
| `web` | `web` | String (URL) | Nein |
| `license` | `license` | String (URL) | Nein |

## Detailliertes Feld-Mapping

### 1. System

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `oparlVersion` | `oparl_version` | String |
| `name` | `name` | String |
| `contactEmail` | `contact_email` | String |
| `contactName` | `contact_name` | String |
| `website` | `website` | String |
| `vendor` | `vendor` | String |
| `product` | `product` | String |
| `otherOparlVersions` | `other_oparl_versions` | String[] |
| `body` | (computed) | URL-Liste |

### 2. Body

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `system` | `system_id` | FK -> System |
| `name` | `name` | String |
| `shortName` | `short_name` | String |
| `website` | `website` | String |
| `ags` | `ags` | String (8-12 Zeichen) |
| `rgs` | `rgs` | String (12-16 Zeichen) |
| `equivalent` | `equivalent` | String[] |
| `contactEmail` | `contact_email` | String |
| `contactName` | `contact_name` | String |
| `classification` | `classification` | String |
| `location` | `location_id` | FK -> Location |
| `organization` | (computed) | URL |
| `person` | (computed) | URL |
| `meeting` | (computed) | URL |
| `paper` | (computed) | URL |
| `legislativeTerm` | (computed) | URL |

### 3. LegislativeTerm

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `body` | `body_id` | FK -> Body |
| `name` | `name` | String |
| `startDate` | `start_date` | Date |
| `endDate` | `end_date` | Date |

### 4. Organization

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `body` | `body_id` | FK -> Body |
| `name` | `name` | String |
| `shortName` | `short_name` | String |
| `organizationType` | `organization_type` | String |
| `post` | `post` | String[] |
| `startDate` | `start_date` | Date |
| `endDate` | `end_date` | Date |
| `externalBody` | `external_body` | String (URL) |
| `website` | `website` | String |
| `classification` | `classification` | String |
| `location` | `location_id` | FK -> Location |
| `membership` | (computed) | URL |
| `meeting` | (M2M) | meeting_organization |

### 5. Person

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `body` | `body_id` | FK -> Body |
| `name` | `name` | String (Anzeigename) |
| `familyName` | `family_name` | String |
| `givenName` | `given_name` | String |
| `formOfAddress` | `form_of_address` | String |
| `affix` | `affix` | String |
| `title` | `title` | String[] |
| `gender` | `gender` | String |
| `phone` | `phone` | String[] |
| `email` | `email` | String[] |
| `streetAddress` | `street_address` | String |
| `postalCode` | `postal_code` | String |
| `locality` | `locality` | String |
| `status` | `status` | String[] |
| `life` | `life` | Text |
| `lifeSource` | `life_source` | String (URL) |
| `location` | `location_id` | FK -> Location |
| `membership` | (Relationship) | Membership[] |

### 6. Membership

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `person` | `person_id` | FK -> Person |
| `organization` | `organization_id` | FK -> Organization |
| `onBehalfOf` | `on_behalf_of_id` | FK -> Organization |
| `role` | `role` | String |
| `votingRight` | `voting_right` | Boolean |
| `startDate` | `start_date` | Date |
| `endDate` | `end_date` | Date |

### 7. Meeting

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `body` | `body_id` | FK -> Body |
| `name` | `name` | String |
| `meetingState` | `meeting_state` | String |
| `cancelled` | `cancelled` | Boolean |
| `start` | `start` | DateTime (TZ) |
| `end` | `end` | DateTime (TZ) |
| `location` | `location_id` | FK -> Location |
| `organization` | (M2M) | meeting_organization |
| `participant` | (M2M) | meeting_participant |
| `invitation` | `invitation_id` | FK -> File |
| `resultsProtocol` | `results_protocol_id` | FK -> File |
| `verbatimProtocol` | `verbatim_protocol_id` | FK -> File |
| `auxiliaryFile` | (M2M) | meeting_auxiliary_file |
| `agendaItem` | (Relationship) | AgendaItem[] |

### 8. AgendaItem

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `meeting` | `meeting_id` | FK -> Meeting |
| `number` | `number` | String |
| `name` | `name` | String |
| `public` | `public` | Boolean |
| `result` | `result` | Text |
| `resolutionText` | `resolution_text` | Text |
| `start` | `start` | DateTime (TZ) |
| `end` | `end` | DateTime (TZ) |
| `consultation` | `consultation_id` | FK -> Consultation |
| `resolutionFile` | `result_file_id` | FK -> File |
| `auxiliaryFile` | (M2M) | agenda_item_auxiliary_file |

### 9. Paper

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `body` | `body_id` | FK -> Body |
| `name` | `name` | String |
| `reference` | `reference` | String |
| `date` | `date` | Date |
| `paperType` | `paper_type` | String |
| `mainFile` | `main_file_id` | FK -> File |
| `auxiliaryFile` | (M2M) | paper_auxiliary_file |
| `originatorPerson` | (M2M) | paper_originator_person |
| `originatorOrganization` | (M2M) | paper_originator_organization |
| `underDirectionOf` | (M2M) | paper_under_direction_organization |
| `consultation` | (Relationship) | Consultation[] |
| `location` | (Relationship) | Location[] |

### 10. Consultation

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `paper` | `paper_id` | FK -> Paper |
| `meeting` | `meeting_id` | FK -> Meeting |
| `authoritative` | `authoritative` | Boolean |
| `role` | `role` | String |
| `organization` | (M2M) | consultation_organization |

### 11. File

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `name` | `name` | String |
| `fileName` | `file_name` | String |
| `mimeType` | `mime_type` | String |
| `date` | `date` | Date |
| `size` | `size` | Integer |
| `sha1Checksum` | `sha1_checksum` | String (40) |
| `sha512Checksum` | `sha512_checksum` | String (128) |
| `text` | `text` | Text |
| `accessUrl` | `access_url` | String (URL) |
| `externalServiceUrl` | `external_service_url` | String (URL) |
| `downloadUrl` | `download_url` | String (URL) |
| `fileLicense` | `file_license` | String (URL) |

Erweiterung: `storage_key` (String) - MinIO Object Key

### 12. Location

| OParl | DB-Spalte | Typ |
|-------|-----------|-----|
| `description` | `description` | Text |
| `streetAddress` | `street_address` | String |
| `room` | `room` | String |
| `postalCode` | `postal_code` | String |
| `locality` | `locality` | String |
| `subLocality` | `sub_locality` | String |
| `geojson` | `geojson` | JSONB (GeoJSON) |

## aitema-Erweiterungen

Zusaetzliche Models ueber den OParl-Standard hinaus:

| Model | Tabelle | Zweck |
|-------|---------|-------|
| `Template` | `template` | Wiederverwendbare Vorlagen-Templates |
| `ApprovalWorkflow` | `approval_workflow` | Mehrstufige Freigabe-Workflows |
| `ApprovalWorkflowStep` | `approval_workflow_step` | Einzelne Workflow-Schritte |
| `ApprovalInstance` | `approval_instance` | Workflow-Instanz fuer eine Vorlage |
| `ApprovalDecision` | `approval_decision` | Einzelne Entscheidung in einem Schritt |
| `Vote` | `vote` | Abstimmung zu einem TOP |
| `IndividualVote` | `individual_vote` | Einzelstimme bei namentlicher Abstimmung |
| `FileVersion` | `file_version` | Dokumenten-Versionierung |
| `Tenant` | `tenant` | Mandanten-Verwaltung (public schema) |

## Many-to-Many Tabellen

| Tabelle | Verknuepft |
|---------|------------|
| `meeting_organization` | Meeting <-> Organization |
| `meeting_participant` | Meeting <-> Person |
| `meeting_auxiliary_file` | Meeting <-> File |
| `paper_originator_person` | Paper <-> Person |
| `paper_originator_organization` | Paper <-> Organization |
| `paper_under_direction_organization` | Paper <-> Organization |
| `paper_auxiliary_file` | Paper <-> File |
| `agenda_item_auxiliary_file` | AgendaItem <-> File |
| `consultation_organization` | Consultation <-> Organization |
