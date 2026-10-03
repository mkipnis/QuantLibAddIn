/* -*- mode: c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */

/*
 Copyright (C) 2005, 2006, 2007 Eric Ehlers
 Copyright (C) 2006, 2007, 2009, 2010 Ferdinando Ametrano
 Copyright (C) 2005 Plamen Neykov
 Copyright (C) 2005 Aurelien Chanudet

 This file is part of QuantLib, a free-software/open-source library
 for financial quantitative analysts and developers - http://quantlib.org/

 QuantLib is free software: you can redistribute it and/or modify it
 under the terms of the QuantLib license.  You should have received a
 copy of the license along with this program; if not, please email
 <quantlib-dev@lists.sf.net>. The license is also available online at
 <http://quantlib.org/license.shtml>.

 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the license for more details.
*/

#ifndef qla_termstructures_hpp
#define qla_termstructures_hpp

#include <qlo/extrapolator.hpp>

namespace QuantLib {

    class TermStructure;

    class OptionletVolatilityStructure;
    class CapFloorTermVolatilityStructure;

    class SwaptionVolatilityStructure;

    class DefaultProbabilityTermStructure;
    class CorrelationTermStructure;

    class InflationTermStructure;

    class VolatilityTermStructure;

    class YieldTermStructure;

}

namespace QuantLibAddin {

    class TermStructure : public ObjectHandler::LibraryObject<QuantLib::TermStructure> {
        protected:
            OH_LIB_CTOR(TermStructure, QuantLib::TermStructure)
    };

class YieldTermStructure : public ObjectHandler::LibraryObject<QuantLib::YieldTermStructure> {
    protected:
        OH_LIB_CTOR(YieldTermStructure, QuantLib::YieldTermStructure)
};

class VolatilityTermStructure : public ObjectHandler::LibraryObject<QuantLib::VolatilityTermStructure> {
    protected:
        OH_LIB_CTOR(VolatilityTermStructure, QuantLib::VolatilityTermStructure)
};


class OptionletVolatilityStructure : public ObjectHandler::LibraryObject<QuantLib::OptionletVolatilityStructure> {
    protected:
        OH_LIB_CTOR(OptionletVolatilityStructure, QuantLib::OptionletVolatilityStructure)
};


class DefaultProbabilityTermStructure : public ObjectHandler::LibraryObject<QuantLib::DefaultProbabilityTermStructure> {
    protected:
        OH_LIB_CTOR(DefaultProbabilityTermStructure, QuantLib::DefaultProbabilityTermStructure)
};

class CorrelationTermStructure : public ObjectHandler::LibraryObject<QuantLib::CorrelationTermStructure>
{
    protected:
        OH_LIB_CTOR( CorrelationTermStructure, QuantLib::CorrelationTermStructure)
    
};


}

namespace QuantLibAddin {
     
    //OH_OBJ_CLASS(TermStructure, Extrapolator);
        //OH_OBJ_CLASS(YieldTermStructure,              TermStructure);
        //OH_OBJ_CLASS(DefaultProbabilityTermStructure, TermStructure);
        //OH_OBJ_CLASS(CorrelationTermStructure, DefaultProbabilityTermStructure);
        OH_OBJ_CLASS(InflationTermStructure,          TermStructure);
        //OH_OBJ_CLASS(VolatilityTermStructure,         VolatilityTermStructure);
            OH_OBJ_CLASS(BlackAtmVolCurve,                VolatilityTermStructure);
                OH_OBJ_CLASS(BlackVolSurface, BlackAtmVolCurve);
                    OH_OBJ_CLASS(InterestRateVolSurface, BlackVolSurface);
            OH_OBJ_CLASS(BlackVolTermStructure,           VolatilityTermStructure);
            OH_OBJ_CLASS(SwaptionVolatilityStructure,     VolatilityTermStructure);
                OH_OBJ_CLASS(SwaptionVolatilityDiscrete, SwaptionVolatilityStructure);
                    OH_OBJ_CLASS(SwaptionVolatilityCube, SwaptionVolatilityDiscrete);
            //OH_OBJ_CLASS(OptionletVolatilityStructure,    OptionletVolatilityStructure);
            OH_OBJ_CLASS(CapFloorTermVolatilityStructure, VolatilityTermStructure);
}

#endif
