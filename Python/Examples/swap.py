import quantlib_addin as qla


def main():
    try:
        # Initialize the environment
        qla.initializeAddin()

        trigger = qla.Property()

        # ------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------

        qla.ohLogSetFile(
            "qlademo.log",
            qla.Property.from_long(4),
            trigger,
        )

        qla.ohLogSetConsole(
            1,
            qla.Property.from_long(4),
            trigger,
        )

        print("Begin example program.")
        print("QuantLibAddin version =", qla.qlAddinVersion(trigger))
        print("ObjectHandler version =", qla.ohVersion(trigger))

        # ------------------------------------------------------------
        # Set the evaluation date to 1 January 2011
        # ------------------------------------------------------------

        evaluation_date = 40546

        qla.qlSettingsSetEvaluationDate(
            qla.Property.from_long(evaluation_date),
            trigger,
        )

        # ------------------------------------------------------------
        # Create the market data objects
        # ------------------------------------------------------------

        market_objects = []

        flat_forward = qla.qlFlatForward(
            "FlatForward",
            qla.Property(),  # NDays
            qla.Property.from_string("NullCalendar"),  # Calendar
            qla.Property.from_double(0.044),  # Rate
            qla.Property(),  # DayCounter
            qla.Property.from_string("Continuous"),  # Compounding
            qla.Property.from_string("Annual"),  # Frequency
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(flat_forward)

        swaption_vts_constant = qla.qlConstantSwaptionVolatility(
            "SwaptionVTSConstant",
            qla.Property(),  # NDays
            "TARGET",  # Calendar
            "f",  # VolType
            qla.Property.from_double(0.15),  # Volatility
            qla.Property(),  # DayCounter
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(swaption_vts_constant)

        euribor = qla.qlEuribor(
            "Euribor",
            "6M",  # Period
            qla.Property.from_string(flat_forward),  # YieldCurve
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(euribor)

        # ------------------------------------------------------------
        # Create schedules
        # ------------------------------------------------------------

        effective_date = 40548
        termination_date = 44201

        schedule1 = qla.qlSchedule(
            "Schedule1",
            qla.Property.from_long(effective_date),
            qla.Property.from_long(termination_date),
            "1Y",
            qla.Property.from_string("TARGET"),
            qla.Property.from_string("Modified Following"),
            qla.Property.from_string("Modified Following"),
            qla.Property.from_string("Backward"),
            qla.Property(),  # FirstDate
            qla.Property(),  # NextToLastDate
            qla.Property(),  # EndOfMonth
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(schedule1)

        schedule2 = qla.qlSchedule(
            "Schedule2",
            qla.Property.from_long(effective_date),
            qla.Property.from_long(termination_date),
            "6M",
            qla.Property.from_string("TARGET"),
            qla.Property.from_string("Modified Following"),
            qla.Property.from_string("Modified Following"),
            qla.Property.from_string("Backward"),
            qla.Property(),  # FirstDate
            qla.Property(),  # NextToLastDate
            qla.Property(),  # EndOfMonth
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(schedule2)

        # ------------------------------------------------------------
        # Create the trade objects
        # ------------------------------------------------------------

        trade_objects = []

        engine = qla.qlDiscountingSwapEngine(
            "DiscountingSwapEngine",
            flat_forward,  # YieldCurve
            qla.Property.from_bool(False),  # IncludeSettlementDateFlows
            qla.Property(),  # SettlementDate
            qla.Property(),  # NpvDate
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(engine)

        coupons = [0.05]
        nominals = [1_000_000]

        fixed_rate_leg = qla.qlFixedRateLeg(
            "FixedRateLeg",
            qla.Property.from_string("Following"),  # PaymentAdjustment
            nominals,  # Nominals
            schedule1,  # Schedule
            coupons,  # Coupons
            "30/360 (Bond Basis)",  # DayCounter
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(fixed_rate_leg)

        fixing_days = []

        ibor_leg = qla.qlIborLeg(
            "IborLeg",
            qla.Property.from_string("Following"),  # PaymentAdjustment
            nominals,  # Nominals
            schedule2,  # Schedule
            fixing_days,  # FixingDays
            qla.Property(),  # FirstFixingDays
            "Actual/360",  # DayCounter
            [],  # Gearings
            [],  # Spreads
            euribor,  # IborIndex
            [],  # Caps
            [],  # Floors
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(ibor_leg)

        leg_ids = [
            fixed_rate_leg,
            ibor_leg,
        ]

        payer = [
            True,
            False,
        ]

        swap = qla.qlSwap(
            "Swap",
            leg_ids,  # LegIDs
            payer,  # Payer
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(swap)

        # ------------------------------------------------------------
        # Set the pricing engine
        # ------------------------------------------------------------

        qla.qlInstrumentSetPricingEngine(
            swap,
            engine,
            trigger,
        )
        # ------------------------------------------------------------
        # Output the PV
        # ------------------------------------------------------------

        print(
            "SWAP PV =",
            qla.qlInstrumentNPV(
                swap,
                trigger,
            ),
        )

        # ------------------------------------------------------------
        # Serialize the objects
        # ------------------------------------------------------------

        qla.ohObjectSave(
            market_objects,
            "MarketData.xml",
            qla.Property.from_bool(True),
            trigger,
            qla.Property.from_bool(True),
        )

        qla.ohObjectSave(
            trade_objects,
            "Swap.xml",
            qla.Property.from_bool(True),
            trigger,
            qla.Property.from_bool(True),
        )

        # ------------------------------------------------------------
        # Example of serializing to/from a buffer
        # ------------------------------------------------------------

        print("Example of serializing to/from a buffer:")

        qla.qlSimpleQuote(
            "quote1",
            qla.Property.from_double(1.42),  # Value
            0,  # TickValue
            qla.Property.from_bool(False),  # Permanent
            trigger,  # Trigger
            False,  # Overwrite
        )

        id_list = ["quote1"]

        xml = qla.ohObjectSaveString(
            id_list,
            qla.Property(),
            qla.Property(),
        )

        print("XML =")
        print(xml)

        id_list2 = qla.ohObjectLoadString(
            xml,
            qla.Property.from_bool(True),
            trigger,
        )

        qla.ohRepositoryLogObject(
            id_list2[0],
            trigger,
        )

        print("End example program.")

    except Exception as e:
        print("Error:", e)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())