/**
 * aitema|RIS - OParl 1.1 TypeScript Type Definitions
 * Complete type definitions for all 12 OParl object types.
 * Based on https://schema.oparl.org/1.1/
 */

// ===================================================================
// Common Base Types
// ===================================================================

/** Common properties shared by all OParl objects */
export interface OParlBase {
  /** OParl ID (URL) */
  id: string;
  /** OParl type URI */
  type: string;
  /** Creation timestamp (ISO 8601) */
  created?: string;
  /** Last modification timestamp (ISO 8601) */
  modified?: string;
  /** Soft-delete flag */
  deleted?: boolean;
  /** Keywords / Tags */
  keyword?: string[];
  /** URL to web representation */
  web?: string;
  /** License URL */
  license?: string;
}

// ===================================================================
// 1. oparl:System
// ===================================================================

export interface OParlSystem extends OParlBase {
  type: "https://schema.oparl.org/1.1/System";
  /** OParl specification version URL */
  oparlVersion: string;
  /** System name */
  name?: string;
  /** Contact email */
  contactEmail?: string;
  /** Contact person name */
  contactName?: string;
  /** System website URL */
  website?: string;
  /** Vendor URL */
  vendor?: string;
  /** Product URL */
  product?: string;
  /** Other supported OParl versions */
  otherOparlVersions?: string[];
  /** URL to the body list */
  body: string;
}

// ===================================================================
// 2. oparl:Body
// ===================================================================

export interface OParlBody extends OParlBase {
  type: "https://schema.oparl.org/1.1/Body";
  /** System URL */
  system: string;
  /** Full name of the body */
  name: string;
  /** Short name */
  shortName?: string;
  /** Website URL */
  website?: string;
  /** Amtlicher Gemeindeschluessel */
  ags?: string;
  /** Regionalschluessel */
  rgs?: string;
  /** Equivalent URIs (e.g., Wikidata) */
  equivalent?: string[];
  /** Contact email */
  contactEmail?: string;
  /** Contact person name */
  contactName?: string;
  /** Classification (Stadt, Gemeinde, Kreis) */
  classification?: string;
  /** Location URL */
  location?: string;
  /** URL to organization list */
  organization: string;
  /** URL to person list */
  person: string;
  /** URL to meeting list */
  meeting: string;
  /** URL to paper list */
  paper: string;
  /** URL to legislative term list */
  legislativeTerm: string;
}

// ===================================================================
// 3. oparl:LegislativeTerm
// ===================================================================

export interface OParlLegislativeTerm extends OParlBase {
  type: "https://schema.oparl.org/1.1/LegislativeTerm";
  /** Body URL */
  body: string;
  /** Name of the legislative term */
  name?: string;
  /** Start date (ISO 8601 date) */
  startDate?: string;
  /** End date (ISO 8601 date) */
  endDate?: string;
}

// ===================================================================
// 4. oparl:Organization
// ===================================================================

export interface OParlOrganization extends OParlBase {
  type: "https://schema.oparl.org/1.1/Organization";
  /** Body URL */
  body: string;
  /** Full name */
  name: string;
  /** Short name */
  shortName?: string;
  /** Type: Rat, Ausschuss, Fraktion, etc. */
  organizationType?: string;
  /** Positions within the organization */
  post?: string[];
  /** Start date */
  startDate?: string;
  /** End date */
  endDate?: string;
  /** External body URL */
  externalBody?: string;
  /** Website URL */
  website?: string;
  /** Classification */
  classification?: string;
  /** Location URL */
  location?: string;
  /** URL to membership list */
  membership: string;
  /** Meeting URLs */
  meeting?: string[];
}

// ===================================================================
// 5. oparl:Person
// ===================================================================

export interface OParlPerson extends OParlBase {
  type: "https://schema.oparl.org/1.1/Person";
  /** Body URL */
  body: string;
  /** Display name */
  name: string;
  /** Family name */
  familyName?: string;
  /** Given name */
  givenName?: string;
  /** Form of address (Anrede) */
  formOfAddress?: string;
  /** Name affix (von, Dr., etc.) */
  affix?: string;
  /** Titles */
  title?: string[];
  /** Gender: female, male, other, none */
  gender?: string;
  /** Phone numbers */
  phone?: string[];
  /** Email addresses */
  email?: string[];
  /** Street address */
  streetAddress?: string;
  /** Postal code */
  postalCode?: string;
  /** City / Locality */
  locality?: string;
  /** Status labels */
  status?: string[];
  /** Short biography */
  life?: string;
  /** Biography source URL */
  lifeSource?: string;
  /** Location URL */
  location?: string;
  /** Membership URLs */
  membership?: string[];
}

// ===================================================================
// 6. oparl:Membership
// ===================================================================

export interface OParlMembership extends OParlBase {
  type: "https://schema.oparl.org/1.1/Membership";
  /** Person URL */
  person: string;
  /** Organization URL */
  organization: string;
  /** On behalf of organization URL */
  onBehalfOf?: string;
  /** Role within the organization */
  role?: string;
  /** Has voting right */
  votingRight?: boolean;
  /** Start date */
  startDate?: string;
  /** End date */
  endDate?: string;
}

// ===================================================================
// 7. oparl:Meeting
// ===================================================================

export interface OParlMeeting extends OParlBase {
  type: "https://schema.oparl.org/1.1/Meeting";
  /** Body URL */
  body: string;
  /** Meeting name */
  name?: string;
  /** Meeting state (eingeladen, durchgefuehrt, abgesagt) */
  meetingState?: string;
  /** Whether meeting is cancelled */
  cancelled?: boolean;
  /** Start datetime (ISO 8601) */
  start?: string;
  /** End datetime (ISO 8601) */
  end?: string;
  /** Location URL */
  location?: string;
  /** Organization URLs */
  organization?: string[];
  /** Participant person URLs */
  participant?: string[];
  /** Invitation file URL */
  invitation?: string;
  /** Results protocol file URL */
  resultsProtocol?: string;
  /** Verbatim protocol file URL */
  verbatimProtocol?: string;
  /** Auxiliary file URLs */
  auxiliaryFile?: string[];
  /** Agenda item URLs */
  agendaItem?: string[];
}

// ===================================================================
// 8. oparl:AgendaItem
// ===================================================================

export interface OParlAgendaItem extends OParlBase {
  type: "https://schema.oparl.org/1.1/AgendaItem";
  /** Meeting URL */
  meeting: string;
  /** Item number (TOP-Nummer) */
  number?: string;
  /** Item name / title */
  name: string;
  /** Whether the item is public */
  public?: boolean;
  /** Result text */
  result?: string;
  /** Resolution text */
  resolutionText?: string;
  /** Start datetime */
  start?: string;
  /** End datetime */
  end?: string;
  /** Consultation URL */
  consultation?: string;
  /** Resolution file URL */
  resolutionFile?: string;
  /** Auxiliary file URLs */
  auxiliaryFile?: string[];
}

// ===================================================================
// 9. oparl:Paper
// ===================================================================

export interface OParlPaper extends OParlBase {
  type: "https://schema.oparl.org/1.1/Paper";
  /** Body URL */
  body: string;
  /** Paper title */
  name: string;
  /** Reference number (Vorlagennummer) */
  reference?: string;
  /** Date (ISO 8601 date) */
  date?: string;
  /** Paper type (Beschlussvorlage, Antrag, etc.) */
  paperType?: string;
  /** Main file URL */
  mainFile?: string;
  /** Auxiliary file URLs */
  auxiliaryFile?: string[];
  /** Originator person URLs */
  originatorPerson?: string[];
  /** Originator organization URLs */
  originatorOrganization?: string[];
  /** Under direction of organization URLs */
  underDirectionOf?: string[];
  /** URL to consultation list */
  consultation: string;
  /** Location URLs */
  location?: string[];
}

// ===================================================================
// 10. oparl:Consultation
// ===================================================================

export interface OParlConsultation extends OParlBase {
  type: "https://schema.oparl.org/1.1/Consultation";
  /** Paper URL */
  paper: string;
  /** Meeting URL */
  meeting?: string;
  /** Whether this is the authoritative consultation */
  authoritative?: boolean;
  /** Role of the consultation */
  role?: string;
  /** Organization URLs */
  organization?: string[];
  /** Agenda item URLs */
  agendaItem?: string[];
}

// ===================================================================
// 11. oparl:File
// ===================================================================

export interface OParlFile extends OParlBase {
  type: "https://schema.oparl.org/1.1/File";
  /** File name / title */
  name?: string;
  /** Original file name */
  fileName?: string;
  /** MIME type */
  mimeType?: string;
  /** Creation date */
  date?: string;
  /** File size in bytes */
  size?: number;
  /** SHA-1 checksum */
  sha1Checksum?: string;
  /** SHA-512 checksum */
  sha512Checksum?: string;
  /** Extracted full text */
  text?: string;
  /** Access URL */
  accessUrl: string;
  /** External service URL (DMS link) */
  externalServiceUrl?: string;
  /** Direct download URL */
  downloadUrl?: string;
  /** File-specific license */
  fileLicense?: string;
}

// ===================================================================
// 12. oparl:Location
// ===================================================================

export interface OParlLocation extends OParlBase {
  type: "https://schema.oparl.org/1.1/Location";
  /** Description */
  description?: string;
  /** Street address */
  streetAddress?: string;
  /** Room */
  room?: string;
  /** Postal code */
  postalCode?: string;
  /** City / Locality */
  locality?: string;
  /** Sub-locality / district */
  subLocality?: string;
  /** GeoJSON geometry object */
  geojson?: GeoJSON.Geometry;
}

// ===================================================================
// Union Types
// ===================================================================

export type OParlObject =
  | OParlSystem
  | OParlBody
  | OParlLegislativeTerm
  | OParlOrganization
  | OParlPerson
  | OParlMembership
  | OParlMeeting
  | OParlAgendaItem
  | OParlPaper
  | OParlConsultation
  | OParlFile
  | OParlLocation;

/** OParl type URI to TypeScript type mapping */
export type OParlTypeMap = {
  "https://schema.oparl.org/1.1/System": OParlSystem;
  "https://schema.oparl.org/1.1/Body": OParlBody;
  "https://schema.oparl.org/1.1/LegislativeTerm": OParlLegislativeTerm;
  "https://schema.oparl.org/1.1/Organization": OParlOrganization;
  "https://schema.oparl.org/1.1/Person": OParlPerson;
  "https://schema.oparl.org/1.1/Membership": OParlMembership;
  "https://schema.oparl.org/1.1/Meeting": OParlMeeting;
  "https://schema.oparl.org/1.1/AgendaItem": OParlAgendaItem;
  "https://schema.oparl.org/1.1/Paper": OParlPaper;
  "https://schema.oparl.org/1.1/Consultation": OParlConsultation;
  "https://schema.oparl.org/1.1/File": OParlFile;
  "https://schema.oparl.org/1.1/Location": OParlLocation;
};
