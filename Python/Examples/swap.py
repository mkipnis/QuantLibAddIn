import quantlib_addin as qla


def main():
    try:
        # Initialize the environment
        qla.initializeAddin()

        # ------------------------------------------------------------
        # Logging
        # ------------------------------------------------------------
        qla.ohLogSetFile("qlademo.log", 4, False,)
        qla.ohLogSetConsole(1, 4, False,)

        print("Begin example program.")
        print("QuantLibAddin version =", qla.qlAddinVersion(False))
        print("ObjectHandler version =", qla.ohVersion(False))

        # ------------------------------------------------------------
        # Set the evaluation date to 1 January 2011
        # ------------------------------------------------------------
        evaluation_date = 40546

        qla.qlSettingsSetEvaluationDate( evaluation_date, False,)
        # ------------------------------------------------------------
        # Create the market data objects
        # ------------------------------------------------------------

        market_objects = []

        flat_forward = qla.qlFlatForward(
            "FlatForward",
            0,  # NDays
            "NullCalendar",  # Calendar
            0.044,  # Rate
            "Actual/365 (Fixed)",  # DayCounter
            "Continuous",  # Compounding
            "Annual",  # Frequency
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(flat_forward)


        swaption_vts_constant = qla.qlConstantSwaptionVolatility(
            "SwaptionVTSConstant",
            0,  # NDays
            "TARGET",
            "Modified Following",
            0.15,  # Volatility
            "Actual/365 (Fixed)",   # DayCounter
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(swaption_vts_constant)

        euribor = qla.qlEuribor(
            "Euribor",
            "6M",  # Period
            flat_forward,  # YieldCurve
            False,  # Permanent
            False,  # Trigger
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
            effective_date,
            termination_date,
            "1Y",
            "TARGET",
            "Modified Following",
            "Modified Following",
            "Backward",
            False,
            None,  # FirstDate
            None,  # NextToLastDate
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )
        market_objects.append(schedule1)


        schedule2 = qla.qlSchedule(
            "Schedule2",
            effective_date,
            termination_date,
            "6M",
            "TARGET",
            "Modified Following",
            "Modified Following",
            "Backward",
            False,  # FirstDate
            None,  # NextToLastDate
            None,  # EndOfMonth
            False,  # Permanent
            False,  # Trigger
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
            False,  # IncludeSettlementDateFlows
            None,  # SettlementDate
            None,  # NpvDate
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(engine)

        coupons = [0.05]
        nominals = [1_000_000]

        fixed_rate_leg = qla.qlFixedRateLeg(
            "FixedRateLeg",
            "Following",  # PaymentAdjustment
            nominals,  # Nominals
            schedule1,  # Schedule
            coupons,  # Coupons
            "30/360 (Bond Basis)",  # DayCounter
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(fixed_rate_leg)

        fixing_days = []

        ibor_leg = qla.qlIborLeg(
            "IborLeg",
            "Following",  # PaymentAdjustment
            nominals,  # Nominals
            schedule2,  # Schedule
            fixing_days,  # FixingDays
            None,  # FirstFixingDays
            "Actual/360",  # DayCounter
            [],  # Gearings
            [],  # Spreads
            euribor,  # IborIndex
            [],  # Caps
            [],  # Floors
            False,  # Permanent
            False,  # Trigger
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
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )
        trade_objects.append(swap)

        # ------------------------------------------------------------
        # Set the pricing engine
        # ------------------------------------------------------------

        qla.qlInstrumentSetPricingEngine(
            swap,
            engine,
            False,
        )
        # ------------------------------------------------------------
        # Output the PV
        # ------------------------------------------------------------

        print(
            "SWAP PV =",
            qla.qlInstrumentNPV(
                swap,
                False,
            ),
        )

        # ------------------------------------------------------------
        # Serialize the objects
        # ------------------------------------------------------------

        qla.ohObjectSave(
            market_objects,
            "MarketData.xml",
            True,
            False,
            True,
        )

        qla.ohObjectSave(
            trade_objects,
            "Swap.xml",
            True,
            False,
            True,
        )

        # ------------------------------------------------------------
        # Example of serializing to/from a buffer
        # ------------------------------------------------------------

        print("Example of serializing to/from a buffer:")

        qla.qlSimpleQuote(
            "quote1",
            1.42,  # Value
            0,  # TickValue
            False,  # Permanent
            False,  # Trigger
            False,  # Overwrite
        )

        id_list = ["quote1"]

        xml = qla.ohObjectSaveString(
            id_list,
            None,
            None,
        )

        print("XML =")
        print(xml)

        id_list2 = qla.ohObjectLoadString(
            xml,
            True,
            False,
        )

        qla.ohRepositoryLogObject(
            id_list2[0],
            False,
        )

        print("End example program.")

    except Exception as e:
        print("Error:", e)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())