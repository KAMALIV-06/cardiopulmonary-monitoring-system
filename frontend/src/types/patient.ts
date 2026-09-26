export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  medical_record_number: string | null;
  baseline_notes?: string | null;
  date_of_birth?: string | null;
  height_cm?: number | null;
  weight_kg?: number | null;
  monitoring_status: string;
  demo_data: boolean;
  created_at: string;
}

export interface MedicalHistoryItem {
  id: number;
  condition_name: string;
  diagnosis_date?: string | null;
  status: string;
  notes?: string | null;
}

export interface MedicationItem {
  id: number;
  medication_name: string;
  dosage: string;
  frequency: string;
  start_date?: string | null;
  end_date?: string | null;
  notes?: string | null;
}

export interface AllergyItem {
  id: number;
  allergen: string;
  reaction: string;
  severity: string;
  notes?: string | null;
}

export interface ClinicalMeasurement {
  id: number;
  measurement_type: string;
  value: number;
  unit: string;
  measured_at: string;
  source: string;
  notes?: string | null;
}

export interface LabResult {
  id: number;
  test_name: string;
  value: number;
  unit: string;
  reference_range?: string | null;
  measured_at: string;
  source: string;
}

export interface PatientEvent {
  id: number;
  event_type: string;
  occurred_at: string;
  summary: string;
  source: string;
}

export interface PatientProfile {
  patient: Patient;
  medical_history: MedicalHistoryItem[];
  medications: MedicationItem[];
  allergies: AllergyItem[];
  clinical_measurements: ClinicalMeasurement[];
  lab_results: LabResult[];
  events: PatientEvent[];
}
