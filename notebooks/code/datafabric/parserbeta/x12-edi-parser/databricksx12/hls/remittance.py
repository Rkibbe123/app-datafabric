from databricksx12.hls.claim import MedicalClaim
import functools


#
# 835 payment information 
#  https://datainsight.health/edi/payments/with-discount/
#
class Remittance(MedicalClaim):

    NAME = "835"

    def __init__(
        self,
        trx_header_loop,
        payer_loop,
        payee_loop,
        clm_loop,
        trx_summary_loop,
        header_number_loop,
    ):
        self.trx_header_loop = trx_header_loop
        self.payer_loop = payer_loop
        self.payee_loop = payee_loop
        self.clm_loop = clm_loop
        self.trx_summary_loop = trx_summary_loop
        self.header_number_loop = header_number_loop
        self.build()

    def build(self):
        self.trx_header_info = self.populate_trx_loop()
        self.payer_info = self.populate_payer_loop()
        self.payee_info = self.populate_payee_loop()
        self.clm_info = self.populate_claim_loop()
        self.plb_info = self.populate_plb_loop()
        self.header_info = self.populate_header_loop()


    def populate_header_loop(self):
        return {
            # LX elements
            "assigned_num": self._first(self.header_number_loop, "LX").element(1),
            # TS3 elements
            "ts3": {
                "provider_identifier": self._first(self.header_number_loop, "TS3").element(1),
                "facility_code_value": self._first(self.header_number_loop, "TS3").element(2),
                "fiscal_period_date": self._first(self.header_number_loop, "TS3").element(3),
                "total_claim_count": self._first(self.header_number_loop, "TS3").element(4),
                "total_claim_change_amount": self._first(self.header_number_loop, "TS3").element(5),
                "total_covered_charge_amount": self._first(self.header_number_loop, "TS3").element(6),
                "total_noncovered_charge_amount": self._first(self.header_number_loop, "TS3").element(7),
                "total_denied_charge_amount": self._first(self.header_number_loop, "TS3").element(8),
                "total_provider_amount": self._first(self.header_number_loop, "TS3").element(9),
                "total_interest_amount": self._first(self.header_number_loop, "TS3").element(10),
                "total_contractual_adjustment_amount": self._first(self.header_number_loop, "TS3").element(11),
                "total_gramm_rudman_reduction_amount": self._first(self.header_number_loop, "TS3").element(12),
                "total_msp_payer_amount": self._first(self.header_number_loop, "TS3").element(13),
                "total_blood_deductible_amount": self._first(self.header_number_loop, "TS3").element(14),
                "total_non_lab_charge_amount": self._first(self.header_number_loop, "TS3").element(15),
                "total_coinsurance_amount": self._first(self.header_number_loop, "TS3").element(16),
                "total_hcpcs_reported_charge_amount": self._first(self.header_number_loop, "TS3").element(17),
                "total_hcpcs_payable_amount": self._first(self.header_number_loop, "TS3").element(18),
                "total_deductible_amount": self._first(self.header_number_loop, "TS3").element(19),
                "total_professional_component_amount": self._first(self.header_number_loop, "TS3").element(20),
                "total_msp_patient_liability_met_amount": self._first(self.header_number_loop, "TS3").element(21),
                "total_patient_reimbursement_amount": self._first(self.header_number_loop, "TS3").element(22),
                "total_pip_claim_count": self._first(self.header_number_loop, "TS3").element(23),
                "total_pip_adjustment_amount": self._first(self.header_number_loop, "TS3").element(24),
            },
            # TS2 elements
            "ts2": {
                "total_drg_amount": self._first(self.header_number_loop, "TS2").element(1),
                "total_federal_specific_amount": self._first(self.header_number_loop, "TS2").element(2),
                "total_hospital_specific_amount": self._first(self.header_number_loop, "TS2").element(3),
                "total_disproportionate_amount": self._first(self.header_number_loop, "TS2").element(4),
                "total_capital_amount": self._first(self.header_number_loop, "TS2").element(5),
                "total_indirect_medical_education_amount": self._first(self.header_number_loop, "TS2").element(6),
                "total_outlier_day_count": self._first(self.header_number_loop, "TS2").element(7),
                "total_day_outlier_amount": self._first(self.header_number_loop, "TS2").element(8),
                "total_cost_outlier_amount": self._first(self.header_number_loop, "TS2").element(9),
                "average_drg_length_of_stay": self._first(self.header_number_loop, "TS2").element(10),
                "total_discharge_count": self._first(self.header_number_loop, "TS2").element(11),
                "total_cost_report_day_count": self._first(self.header_number_loop, "TS2").element(12),
                "total_covered_day_count": self._first(self.header_number_loop, "TS2").element(13),
                "total_noncovered_day_count": self._first(self.header_number_loop, "TS2").element(14),
                "total_msp_pass_through_amount": self._first(self.header_number_loop, "TS2").element(15),
                "average_drg_weight": self._first(self.header_number_loop, "TS2").element(16),
                "total_pps_capital_fsp_drg_amount": self._first(self.header_number_loop, "TS2").element(17),
                "total_psp_capital_hsp_drg_amount": self._first(self.header_number_loop, "TS2").element(18),
                "total_pps_dsh_drg_amount": self._first(self.header_number_loop, "TS2").element(19),
            },
        }


    def populate_plb_loop(self):
        return functools.reduce(
            lambda x, y: x + y,
            [
                [
                    {
                        'provider_identifier': p.element(1),
                        'fiscal_period_date': p.element(2),
                        'provider_adjustment_reason_cd_1': p.element(3, 0) if p.segment_len() > 3 else None,
                        'provider_adjustment_id_1': p.element(3, 1) if p.segment_len() > 3 else None,
                        'provider_adjustment_amt_1': p.element(4) if p.segment_len() > 4 else None,
                        'provider_adjustment_reason_cd_2': p.element(5, 0) if p.segment_len() > 5 else None,
                        'provider_adjustment_id_2': p.element(5, 1) if p.segment_len() > 5 else None,
                        'provider_adjustment_amt_2': p.element(6) if p.segment_len() > 6 else None,
                        'provider_adjustment_reason_cd_3': p.element(7, 0) if p.segment_len() > 7 else None,
                        'provider_adjustment_id_3': p.element(7, 1) if p.segment_len() > 7 else None,
                        'provider_adjustment_amt_3': p.element(8) if p.segment_len() > 8 else None,
                        'provider_adjustment_reason_cd_4': p.element(9, 0) if p.segment_len() > 9 else None,
                        'provider_adjustment_id_4': p.element(9, 1) if p.segment_len() > 9 else None,
                        'provider_adjustment_amt_4': p.element(10) if p.segment_len() > 10 else None,
                        'provider_adjustment_reason_cd_5': p.element(11, 0) if p.segment_len() > 11 else None,
                        'provider_adjustment_id_5': p.element(11, 1) if p.segment_len() > 11 else None,
                        'provider_adjustment_amt_5': p.element(12) if p.segment_len() > 12 else None,
                        'provider_adjustment_reason_cd_6': p.element(13, 0) if p.segment_len() > 13 else None,
                        'provider_adjustment_id_6': p.element(13, 1) if p.segment_len() > 13 else None,
                        'provider_adjustment_amt_6': p.element(14) if p.segment_len() > 14 else None,
                    }
                    for p in self.segments_by_name("PLB", data=self.trx_summary_loop)
                ],
                [],
            ]
        )



    def populate_payer_loop(self):
        return {
            "entity_identifier_code": self._first(self.payer_loop, "N1").element(1),
            "payer_name": self._first(self.payer_loop, "N1").element(2),
            "id_code_qualifier": self._first(self.payer_loop, "N1").element(3),
            "payer_identifier": self._first(self.payer_loop, "N1").element(4),
            "entity_relationship_code": self._first(self.payer_loop, "N1").element(5),
            "payer_address_line_1": self._first(self.payer_loop, "N3").element(1),
            "payer_address_line_2": self._first(self.payer_loop, "N3").element(2),
            "payer_city_name": self._first(self.payer_loop, "N4").element(1),
            "payer_state_code": self._first(self.payer_loop, "N4").element(2),
            "payer_postal_zone_or_zip_code": self._first(self.payer_loop, "N4").element(3),
            "country_code": self._first(self.payer_loop, "N4").element(4),
            "location_qualifier": self._first(self.payer_loop, "N4").element(5),
            "country_subdivision_code": self._first(self.payer_loop, "N4").element(7),
            "payer_contact_info": [
                {
                    "contact_function_cd": c.element(1),
                    "contact_name": c.element(2),
                    "communication_number_qualifier1": c.element(3),
                    "contact_communication1": c.element(4),
                    "communication_number_qualifier2": c.element(5),
                    "contact_communication2": c.element(6),
                    "communication_number_qualifier3": c.element(7),
                    "contact_communication3": c.element(8),
                    "contact_inquiry_reference": c.element(9),
                }
                for c in self.segments_by_name("PER", data=self.payer_loop)
            ],
            "payer_additional_identification": [
                {
                    "id_qualifier_code": c.element(1),
                    "id": c.element(2),
                    "description": c.element(3),
                }
                for c in self.segments_by_name("REF", data=self.payer_loop)
            ],
        }

    def populate_payee_loop(self):
        return {
            "entity_identifier_code": self._first(self.payee_loop, "N1").element(1),
            "payee_name": self._first(self.payee_loop, "N1").element(2),
            "id_code_qualifier": self._first(self.payee_loop, "N1").element(3),
            "payee_identifier": self._first(self.payee_loop, "N1").element(4),
            "entity_relationship_code": self._first(self.payee_loop, "N1").element(5),
            "payee_address_line_1": self._first(self.payee_loop, "N3").element(1),
            "payee_address_line_2": self._first(self.payee_loop, "N3").element(2),
            "payee_city_name": self._first(self.payee_loop, "N4").element(1),
            "payee_state_code": self._first(self.payee_loop, "N4").element(2),
            "payee_postal_zone_or_zip_code": self._first(self.payee_loop, "N4").element(3),
            "country_code": self._first(self.payee_loop, "N4").element(4),
            "location_qualifier": self._first(self.payee_loop, "N4").element(5),
            "country_subdivision_code": self._first(self.payee_loop, "N4").element(7),
            "payee_additional_identification": [
                {
                    "id_qualifier_code": c.element(1),
                    "id": c.element(2),
                    "description": c.element(3),
                }
                for c in self.segments_by_name("REF", data=self.payee_loop)
            ],
            "delivery_report_transmission_code": self._first(self.payee_loop, "RDM").element(1),
            "delivery_name": self._first(self.payee_loop, "RDM").element(2),
            "delivery_communication_number": self._first(self.payee_loop, "RDM").element(3),
            "delivery_reference_identifier": self._first(self.payee_loop, "RDM").element(4),
        }

    def populate_trx_loop(self):
        return {
            "dtm": {
                "date_code": self._first(self.trx_header_loop, "DTM").element(1),
                "date": self._first(self.trx_header_loop, "DTM").element(2),
                "time": self._first(self.trx_header_loop, "DTM").element(3),
            },
            "bpr": {
                "transaction_handling_code": self._first(self.trx_header_loop, "BPR").element(1),
                "total_actual_provider_payment_amt": self._first(self.trx_header_loop, "BPR").element(2),
                "creditor_debit_flag_code": self._first(self.trx_header_loop, "BPR").element(3),
                "payment_method_code": self._first(self.trx_header_loop, "BPR").element(4),
                "payment_format_code": self._first(self.trx_header_loop, "BPR").element(5),
                "sender_dfiid_number_qualifier": self._first(self.trx_header_loop, "BPR").element(6),
                "sender_dfi_identifier": self._first(self.trx_header_loop, "BPR").element(7),
                "sender_account_number_qualifier": self._first(self.trx_header_loop, "BPR").element(8),
                "sender_bank_acct_number": self._first(self.trx_header_loop, "BPR").element(9),
                "payer_identifier": self._first(self.trx_header_loop, "BPR").element(10),
                "payer_originating_co_supplemental_code": self._first(self.trx_header_loop, "BPR").element(11),
                "receiver_dfiid_number_qualifier": self._first(self.trx_header_loop, "BPR").element(12),
                "receiver_or_provider_bank_id_number": self._first(self.trx_header_loop, "BPR").element(13),
                "receiver_acct_number_qualifier": self._first(self.trx_header_loop, "BPR").element(14),
                "receiver_or_provider_account_number": self._first(self.trx_header_loop, "BPR").element(15),
                "check_issue_or_eft_effective_date": self._first(self.trx_header_loop, "BPR").element(16),
                "business_function_code": self._first(self.trx_header_loop, "BPR").element(17), 
            },
            "trn": {
                "trace_type_code": self._first(self.trx_header_loop, "TRN").element(1),
                "check_or_eft_trace_number": self._first(self.trx_header_loop, "TRN").element(2),
                "trace_payer_identifier": self._first(self.trx_header_loop, "TRN").element(3),
                "trace_payer_originating_co_supplemental_code": self._first(self.trx_header_loop, "TRN").element(4),
            }
        }

    def populate_claim_loop(self):
        end_clp_index = (
            [
                i
                for i, z in enumerate([y.segment_name() for y in self.clm_loop[1:]])
                if z == "CLP"
            ]
            + [len(self.clm_loop)]
        )[0]
        return {
            "clp": {
                "patient_control_number": self._first(self.clm_loop, "CLP").element(1),
                "claim_status_code": self._first(self.clm_loop, "CLP").element(2),
                "total_claim_charge_amount": self._first(self.clm_loop, "CLP").element(3),
                "claim_payment_amount": self._first(self.clm_loop, "CLP").element(4),
                "patient_responsibility_amount": self._first(self.clm_loop, "CLP").element(5),
                "claim_filing_indicator_code": self._first(self.clm_loop, "CLP").element(6),
                "payer_claim_control_number": self._first(self.clm_loop, "CLP").element(7),
                "facility_code_value": self._first(self.clm_loop, "CLP").element(8),
                "claim_frequency_code": self._first(self.clm_loop, "CLP").element(9),
                "patient_status_code": self._first(self.clm_loop, "CLP").element(10),
                "drg_code": self._first(self.clm_loop, "CLP").element(11),
                "drg_weight": self._first(self.clm_loop, "CLP").element(12),
                "discharge_fraction": self._first(self.clm_loop, "CLP").element(13),
                "yes_no_condition_or_response_code": self._first(self.clm_loop, "CLP").element(14),
            },
            "first_nm1_patient": {
                "entity_identifier_code": self._first(self.clm_loop, "NM1").element(1),
                "entity_type_qualifier": self._first(self.clm_loop, "NM1").element(2),
                "last_name_or_organization": self._first(self.clm_loop, "NM1").element(3),
                "first_name": self._first(self.clm_loop, "NM1").element(4),
                "middle_name": self._first(self.clm_loop, "NM1").element(5),
                "name_prefix": self._first(self.clm_loop, "NM1").element(6),
                "name_suffix": self._first(self.clm_loop, "NM1").element(7),
                "id_code_qualifier": self._first(self.clm_loop, "NM1").element(8),
                "identifier": self._first(self.clm_loop, "NM1").element(9),
                "entity_relationship_code": self._first(self.clm_loop, "NM1").element(10),
            },
            "claim_names": self._populate_names(self.clm_loop[:end_clp_index]),
            "claim_contacts": [
                {
                    "contact_function_cd": c.element(1),
                    "contact_name": c.element(2),
                    "communication_number_qualifier1": c.element(3),
                    "contact_communication1": c.element(4),
                    "communication_number_qualifier2": c.element(5),
                    "contact_communication2": c.element(6),
                    "communication_number_qualifier3": c.element(7),
                    "contact_communication3": c.element(8),
                    "contact_inquiry_reference": c.element(9),
                }
                for c in self.segments_by_name(
                    "PER",
                    data=self.clm_loop[: self.index_of_segment(self.clm_loop, "SVC")],
                )
            ],
            "mia": {
                "covered_days_or_visits_count": self._first(self.clm_loop, "MIA").element(1),
                "pps_operation_outlier_amount": self._first(self.clm_loop, "MIA").element(2),
                "lifetime_psychiatric_days_count": self._first(self.clm_loop, "MIA").element(3),
                "claim_drg_amount": self._first(self.clm_loop, "MIA").element(4),
                "claim_payment_remark_code": self._first(self.clm_loop, "MIA").element(5),
                "claim_dsh_amount": self._first(self.clm_loop, "MIA").element(6),
                "claim_msp_pass_thru_amount": self._first(self.clm_loop, "MIA").element(7),
                "claim_pps_capital_amount": self._first(self.clm_loop, "MIA").element(8),
                "pps_capital_fsp_drg_amount": self._first(self.clm_loop, "MIA").element(9),
                "pps_capital_hsp_drg_amount": self._first(self.clm_loop, "MIA").element(10),
                "pps_capital_dsh_drg_amount": self._first(self.clm_loop, "MIA").element(11),
                "old_capital_amount": self._first(self.clm_loop, "MIA").element(12),
                "pps_capital_ime_amount": self._first(self.clm_loop, "MIA").element(13),
                "pps_oper_hsp_spec_drg_amount": self._first(self.clm_loop, "MIA").element(14),
                "cost_report_day_count": self._first(self.clm_loop, "MIA").element(15),
                "pps_oper_fsp_spec_drg_amount": self._first(self.clm_loop, "MIA").element(16),
                "claim_pps_outlier_amount": self._first(self.clm_loop, "MIA").element(17),
                "claim_indirect_teaching": self._first(self.clm_loop, "MIA").element(18),
                "non_pay_prof_comp_amount": self._first(self.clm_loop, "MIA").element(19),
                "inpatient_claim_payment_remark_code_1": self._first(self.clm_loop, "MIA").element(20),
                "inpatient_claim_payment_remark_code_2": self._first(self.clm_loop, "MIA").element(21),
                "inpatient_claim_payment_remark_code_3": self._first(self.clm_loop, "MIA").element(22),
                "inpatient_claim_payment_remark_code_4": self._first(self.clm_loop, "MIA").element(23),
                "pps_capital_exception_amount": self._first(self.clm_loop, "MIA").element(24),
            },
            "moa": {
                "reimbursement_rate": self._first(self.clm_loop, "MOA").element(1),
                "claim_hcpcs_payable_amount": self._first(self.clm_loop, "MOA").element(2),
                "outpatient_claim_payment_remark_code_1": self._first(self.clm_loop, "MOA").element(3),
                "outpatient_claim_payment_remark_code_2": self._first(self.clm_loop, "MOA").element(4),
                "outpatient_claim_payment_remark_code_3": self._first(self.clm_loop, "MOA").element(5),
                "outpatient_claim_payment_remark_code_4": self._first(self.clm_loop, "MOA").element(6),
                "outpatient_claim_payment_remark_code_5": self._first(self.clm_loop, "MOA").element(7),
                "claim_esrd_payment_amount": self._first(self.clm_loop, "MOA").element(8),
                "non_payable_professional_comp_amount": self._first(self.clm_loop, "MOA").element(9),
            },
            "claim_related_identifications": [
                {
                    "id_qualifier_code": x.element(1),
                    "id": x.element(2),
                    "description": x.element(3),
                }
                for x in self.segments_by_name(
                    "REF",
                    data=self.clm_loop[: self.index_of_segment(self.clm_loop, "SVC")],
                )
            ],
            "claim_supplemental_amount": [
                {
                    "amount_qualifier_code": x.element(1),
                    "amt": x.element(2),
                    "credit_debit_flag_code": x.element(3),
                }
                for x in self.segments_by_name(
                    "AMT",
                    data=self.clm_loop[: self.index_of_segment(self.clm_loop, "SVC")],
                )
            ],
            "claim_supplemental_quantity": [
                {
                    "quantity_qualifier_code": x.element(1),
                    "qty": x.element(2),
                    "composite_unit_of_measure": x.element(3),
                }
                for x in self.segments_by_name(
                    "QTY",
                    data=self.clm_loop[: self.index_of_segment(self.clm_loop, "SVC")],
                )
            ],
            # Claim level service adjustments CAS
            "claim_adjustments": functools.reduce(
                lambda x, y: x + y,
                [
                    self.populate_adjustment_groups(x)
                    for x in self.segments_by_name(
                        "CAS",
                        data=self.clm_loop[
                            1 : min(
                                list(
                                    filter(
                                        lambda x: x >= 0,
                                        [
                                            self.index_of_segment(self.clm_loop, "SVC"),
                                            len(self.clm_loop) - 1,
                                        ],
                                    )
                                )
                            )
                        ],
                    )
                ],
                [],
            ),
            "claim_lines": [
                self.populate_claim_line(
                    seg,
                    i,
                    min(
                        self.index_of_segment(self.clm_loop, "SVC", i + 1),
                        len(self.clm_loop) - 1,
                    ),
                )
                for i, seg in self.segments_by_name_index(
                    segment_name="SVC", data=self.clm_loop
                )
            ],
            "claim_dates": [
                {
                    "date_code": x.element(1),
                    "date": x.element(2),
                    "time": x.element(3),
                }
                for x in self.clm_loop
                if x.segment_name() == "DTM"
            ],
        }

    def _populate_names(self, loop):
        return [
            {
                "entity_identifier_code": x.element(1),
                "entity_type_qualifier": x.element(2),
                "last_name_or_organization": x.element(3),
                "first_name": x.element(4),
                "middle_name": x.element(5),
                "name_prefix": x.element(6),
                "name_suffix": x.element(7),
                "id_code_qualifier": x.element(8),
                "identifier": x.element(9),
                "entity_relationship_code": x.element(10),
            }
            for x in loop
            if x.segment_name() == "NM1"
        ]

    #
    # @parma svc - the svc segment for the service rendered
    # @param idx - the index where the svc is found within self.clm_loop
    # @param svc_end_idx - the last segment associated with the service
    #
    def populate_claim_line(self, svc, idx, svc_end_idx):
        return {
            "claim_line_details": {
                "prcdr_cd": svc.element(1),
                "chrg_amt": svc.element(2),
                "paid_amt": svc.element(3),
                "rev_cd": svc.element(4),
                "units": svc.element(5),
                "original_prcdr_cd": svc.element(6),
                "original_units_of_service_count": svc.element(7),
            },
            "claim_line_dates": {
                "date_code": self._first(self.clm_loop, "DTM", idx).element(1),
                "date": self._first(self.clm_loop, "DTM", idx).element(2),
                "time": self._first(self.clm_loop, "DTM", idx).element(3),
            },
            "claim_line_supplemental_amount": [
                {
                    "amt_qualifier_cd": a.element(1),
                    "amt": a.element(2),
                    "credit_debit_flag_code": a.element(3),
                }
                for a in self.segments_by_name(
                    "AMT", data=self.clm_loop[idx:svc_end_idx]
                )
            ],
            "claim_line_supplemental_quantity": [
                {
                    "quantity_qualifier": a.element(1),
                    "qty": a.element(2),
                    "composite_unit_of_measure": a.element(3),
                }
                for a in self.segments_by_name(
                    "AMT", data=self.clm_loop[idx:svc_end_idx]
                )
            ],
            "claim_line_remarks": [
                {"qualifier_cd": x.element(1), "remark_cd": x.element(2)}
                for x in self.segments_by_name(
                    "LQ", data=self.clm_loop[idx:svc_end_idx]
                )
            ],
            # line level service adjustments
            "claim_line_adjustments": functools.reduce(
                lambda x, y: x + y,
                [
                    self.populate_adjustment_groups(x)
                    for x in self.segments_by_name(
                        "CAS", data=self.clm_loop[idx:svc_end_idx]
                    )
                ],
                [],
            ),
            "claim_line_related_identifications": [
                {
                    "id_code_qualifier": x.element(1),
                    "id": x.element(2),
                    "description": x.element(3),
                }
                for x in self.segments_by_name(
                    "REF", data=self.clm_loop[idx:svc_end_idx]
                )
            ],
        }

    #
    # group adjustment logic
    #

    # def populate_adjustment_groups(self, cas):
    #     return [
    #         {
    #             "adjustment_grp_cd": (
    #                 cas.element(1) if cas.element(i) == "" else cas.element(i)
    #             ),
    #             "adjustment_reason_cd": cas.element(i + 1),
    #             "adjustment_amount": cas.element(i + 2),
    #         }
    #         for i in list(range(1, cas.segment_len() - 1, 3))
    #     ]

    def populate_adjustment_groups(self, cas):
        group_code = cas.element(1)
        return [
            {
                "adjustment_grp_cd": group_code,
                "adjustment_reason_cd_1": cas.element(2),
                "adjustment_amount_1": cas.element(3),
                "adjustment_quantity_1": cas.element(4),
                "adjustment_reason_cd_2": cas.element(5),
                "adjustment_amount_2": cas.element(6),
                "adjustment_quantity_2": cas.element(7),
                "adjustment_reason_cd_3": cas.element(8),
                "adjustment_amount_3": cas.element(9),
                "adjustment_quantity_3": cas.element(10),
                "adjustment_reason_cd_4": cas.element(11),
                "adjustment_amount_4": cas.element(12),
                "adjustment_quantity_4": cas.element(13),
                "adjustment_reason_cd_5": cas.element(14),
                "adjustment_amount_5": cas.element(15),
                "adjustment_quantity_5": cas.element(16),
                "adjustment_reason_cd_6": cas.element(17),
                "adjustment_amount_6": cas.element(18),
                "adjustment_quantity_6": cas.element(19),
            }
        ]

    def to_json(self):
        return {
            **{"payment": self.trx_header_info},
            **{"payer": self.payer_info},
            **{"payee": self.payee_info},
            **{"claim": self.clm_info},
            **{"provider_adjustments": self.plb_info},
            **{"header_info": self.header_info},
        }