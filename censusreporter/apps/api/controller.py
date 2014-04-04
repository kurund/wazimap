from collections import OrderedDict

from .models import get_model_from_fields
from .utils import get_session


class LocationNotFound(Exception):
    pass


PROFILE_SECTIONS = (
    'demographics',  # population group, age group in 5 years, age in completed years
    'economics',  # individual monthly income, type of sector, official employment status
    'sanitation',  # source of water, refuse disposal
    'education',  # highest educational level
)

# Education categories

COLLAPSED_EDUCATION_CATEGORIES = {
    'Gade 0': '<= Gr 3',
    'Grade 1 / Sub A': '<= Gr 3',
    'Grade 2 / Sub B': '<= Gr 3',
    'Grade 3 / Std 1/ABET 1Kha Ri Gude;SANLI': '<= Gr 3',
    'Grade 4 / Std 2': 'GET',
    'Grade 5 / Std 3/ABET 2': 'GET',
    'Grade 6 / Std 4': 'GET',
    'Grade 7 / Std 5/ ABET 3': 'GET',
    'Grade 8 / Std 6 / Form 1': 'GET',
    'Grade 9 / Std 7 / Form 2/ ABET 4': 'GET',
    'Grade 10 / Std 8 / Form 3': 'FET',
    'Grade 11 / Std 9 / Form 4': 'FET',
    'Grade 12 / Std 10 / Form 5': 'FET',
    'NTC I / N1/ NIC/ V Level 2': 'FET',
    'NTC II / N2/ NIC/ V Level 3': 'FET',
    'NTC III /N3/ NIC/ V Level 4': 'FET',
    'N4 / NTC 4': 'FET',
    'N5 /NTC 5': 'HET',
    'N6 / NTC 6': 'HET',
    'Certificate with less than Grade 12 / Std 10': 'FET',
    'Diploma with less than Grade 12 / Std 10': 'FET',
    'Certificate with Grade 12 / Std 10': 'HET',
    'Diploma with Grade 12 / Std 10': 'HET',
    'Higher Diploma': 'HET',
    'Post Higher Diploma Masters; Doctoral Diploma': 'Post-grad',
    'Bachelors Degree': 'HET',
    'Bachelors Degree and Post graduate Diploma': 'Post-grad',
    'Honours degree': 'Post-grad',
    'Higher Degree Masters / PhD': 'Post-grad',
    'Other': 'Other',
    'No schooling': 'None',
    'Unspecified': 'Other',
    'Not applicable': 'Other',
}
EDUCATION_GET_OR_HIGHER = set([
    'Grade 9 / Std 7 / Form 2/ ABET 4',
    'Grade 10 / Std 8 / Form 3',
    'Grade 11 / Std 9 / Form 4',
    'Grade 12 / Std 10 / Form 5',
    'NTC I / N1/ NIC/ V Level 2',
    'NTC II / N2/ NIC/ V Level 3',
    'NTC III /N3/ NIC/ V Level 4',
    'N4 / NTC 4',
    'N5 /NTC 5',
    'N6 / NTC 6',
    'Certificate with less than Grade 12 / Std 10',
    'Diploma with less than Grade 12 / Std 10',
    'Certificate with Grade 12 / Std 10',
    'Diploma with Grade 12 / Std 10',
    'Higher Diploma',
    'Post Higher Diploma Masters; Doctoral Diploma',
    'Bachelors Degree',
    'Bachelors Degree and Post graduate Diploma',
    'Honours degree',
    'Higher Degree Masters / PhD',
])
EDUCATION_FET_OR_HIGHER = set([
    'Grade 12 / Std 10 / Form 5',
    'N4 / NTC 4',
    'N5 /NTC 5',
    'N6 / NTC 6',
    'Certificate with Grade 12 / Std 10',
    'Diploma with Grade 12 / Std 10',
    'Higher Diploma',
    'Post Higher Diploma Masters; Doctoral Diploma',
    'Bachelors Degree',
    'Bachelors Degree and Post graduate Diploma',
    'Honours degree',
    'Higher Degree Masters / PhD',
])

# Age categories

COLLAPSED_AGE_CATEGORIES = {
    '00 - 04': '0-9',
    '05 - 09': '0-9',
    '10 - 14': '10-19',
    '15 - 19': '10-19',
    '20 - 24': '20-29',
    '25 - 29': '20-29',
    '30 - 34': '30-39',
    '35 - 39': '30-39',
    '40 - 44': '40-49',
    '45 - 49': '40-49',
    '50 - 54': '50-59',
    '55 - 59': '50-59',
    '60 - 64': '60-69',
    '65 - 69': '60-69',
    '70 - 74': '70-79',
    '75 - 79': '70-79',
    '80 - 84': '80+',
    '85+': '80+',
}

# Income categories

COLLAPSED_INCOME_CATEGORIES = {
    "No income": "0k",
    "Not applicable": "N/A",
    "R 102 401 - R 204 800": "> 102.4k",
    "R 12 801 - R 25 600": "51.2k",
    "R 1 601 - R 3 200": "3.2k",
    "R 1 - R 400": "0.8k",
    "R 204 801 or more": "> 102.4k",
    "R 25 601 - R 51 200": "51.2k",
    "R 3 201 - R 6 400": "6.4k",
    "R 401 - R 800": "0.8k",
    "R 51 201 - R 102 400": "102.4k",
    "R 6 401 - R 12 800": "12.8k",
    "R 801 - R 1 600": "1.6k",
    "Unspecified": "Unspec.",
}


def get_profile(geo_code, geo_level):
    session = get_session()
    data = {}
    for section in PROFILE_SECTIONS:
        function_name = 'get_%s_profile' % section
        if function_name in globals():
            data[section] = globals()[function_name](geo_code, geo_level, session)

    data['geography'] = {
        'this': {},
        'parents': {},
    }
    
    session.close()
    return data


def get_demographics_profile(geo_code, geo_level, session):
    # population group
    db_model_pop = get_model_from_fields(['population group'], geo_level)
    objects = get_objects_by_geo(db_model_pop, geo_code, geo_level,
                                 session, order_by='population group')

    pop_dist_data = OrderedDict()
    total_pop = 0.0
    for obj in objects:
        pop_group = getattr(obj, 'population group')
        total_pop += obj.total
        pop_dist_data[pop_group] = {
            "name": pop_group,
            "numerators": {"this": obj.total},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        }

    # age groups
    db_model_age = get_model_from_fields(['age groups in 5 years'], geo_level)
    objects = get_objects_by_geo(db_model_age, geo_code, geo_level, session)

    age_dist_data = {}
    total_age = 0.0
    for obj in objects:
        age_group = getattr(obj, 'age groups in 5 years')
        total_age += obj.total
        age_dist_data[age_group] = {
            "name": age_group,
            "numerators": {"this": obj.total},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        }
    age_dist_data = collapse_categories(age_dist_data,
                                        COLLAPSED_AGE_CATEGORIES,
                                        key_order=('0-9', '10-19',
                                                   '20-29', '30-39',
                                                   '40-49', '50-59',
                                                   '60-69', '70-79',
                                                   '80+'))

    # calculate percentages
    for data, total in zip((pop_dist_data, age_dist_data),
                           (total_pop, total_age)):
        for fields in data.values():
            fields["values"] = {"this": round(fields["numerators"]["this"]
                                              / total * 100, 2)}

    final_data = {'population_group_distribution': pop_dist_data,
                  'age_group_distribution': age_dist_data}

    # median age/age category if possible (might not have data at ward level)
    try:
        db_model_age = get_model_from_fields(['age in completed years'], geo_level)
        objects = sorted(
            get_objects_by_geo(db_model_age, geo_code, geo_level, session),
            key=lambda x: int(getattr(x, 'age in completed years'))
        )
        # median age
        median = calculate_median(objects, 'age in completed years')
        final_data['median_age'] = {
            "name": "Median age",
            "values": {"this": median},
            "error": {"this": 0.0},
            "numerators": {"this": sum(x.total for x in objects)},
            "numerator_errors": {"this": 0.0},
        }
        # age category
        under_18 = 0.0
        over_or_65 = 0.0
        between_18_64 = 0.0
        total = 0.0
        for obj in objects:
            age = int(getattr(obj, 'age in completed years'))
            total += obj.total
            if age < 18:
                under_18 += obj.total
            elif age >= 65:
                over_or_65 += obj.total
            else:
                between_18_64 += obj.total
        final_data['age_category_distribution'] = OrderedDict((
            ("under_18", {
                "name": "Under 18",
                "error": {"this": 0.0},
                "values": {"this": round(under_18 / total, 2)},
                "numerators": {"this": total},
                "numerator_errors": {"this": 0.0},
            }),
            ("18_to_64", {
                "name": "18 to 64",
                "error": {"this": 0.0},
                "values": {"this": round(between_18_64 / total, 2)},
                "numerators": {"this": total},
                "numerator_errors": {"this": 0.0},
            }),
            ("65_and_over", {
                "name": "65 and over",
                "error": {"this": 0.0},
                "values": {"this": round(over_or_65 / total, 2)},
                "numerators": {"this": total},
                "numerator_errors": {"this": 0.0},
            })
        ))
    except LocationNotFound:
        final_data['median_age'] = {
            "name": "Median age",
            "error": {"this": 0.0},
            "numerators": {"this": 0},
            "numerator_errors": {"this": 0.0},
        }
        final_data['age_category_distribution'] = {
            "": {
                "name": "N/A",
                "error": {"this": 0.0},
                "values": {"this": 0},
                "numerators": {"this": 0},
                "numerator_errors": {"this": 0.0},
            }
        }

    return final_data


def get_economics_profile(geo_code, geo_level, session):
    # income
    db_model_income = get_model_from_fields(['individual monthly income'],
                                            geo_level,
                                            'individualmonthlyincome_%s_employedonly'
                                            % geo_level)
    objects = get_objects_by_geo(db_model_income, geo_code, geo_level, session)
    income_dist_data = {}
    total_income = 0.0
    for obj in objects:
        income_group = getattr(obj, 'individual monthly income')
        if income_group == 'Not applicable':
            continue
        total_income += obj.total
        income_dist_data[income_group] = {
            "name": income_group,
            "numerators": {"this": obj.total},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        }
    income_dist_data = collapse_categories(income_dist_data,
                                           COLLAPSED_INCOME_CATEGORIES,
                                           key_order=('Unspec.', '0k',
                                                      '0.8k', '1.6k', '3.2k',
                                                      '6.4k', '12.8k', '51.2k',
                                                      '102.4k', '> 102.4k'))

    db_model_employ = get_model_from_fields(['official employment status'],
                                            geo_level)
    objects = get_objects_by_geo(db_model_employ, geo_code, geo_level, session)
    employ_status = {}
    total_workers = 0.0
    for obj in objects:
        employ_st = getattr(obj, 'official employment status')
        if employ_st in ('Age less than 15 years', 'Not applicable'):
            continue
        total_workers += obj.total
        employ_status[employ_st] = {
            "name": employ_st,
            "numerators": {"this": obj.total},
            "error": {"this": 0.0}
        }

    # sector
    db_model_sector = get_model_from_fields(['type of sector'], geo_level)
    objects = get_objects_by_geo(db_model_sector, geo_code, geo_level,
                                 session, order_by='type of sector')
    sector_dist_data = OrderedDict()
    total_sector = 0.0
    for obj in objects:
        sector = getattr(obj, 'type of sector')
        if sector == 'Not applicable' or obj.total == 0:
            continue
        total_sector += obj.total
        sector_dist_data[sector] = {
            "name": sector,
            "numerators": {"this": obj.total},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        }

    for data, total in zip((income_dist_data, sector_dist_data, employ_status),
                           (total_income, total_sector, total_workers)):
        for fields in data.values():
            fields["values"] = {"this": round(fields["numerators"]["this"]
                                              / total * 100, 2)}

    income_dist_data['metadata'] = {'universe': 'Officially employed individuals'}
    employ_status['metadata'] = {'universe': 'Workers 15 and over'}

    return {'individual_income_distribution': income_dist_data,
            'employment_status': employ_status,
            'sector_type_distribution': sector_dist_data}


'''
def get_sanitation_profile(geo_code, geo_level, session):
    pass
'''


def get_education_profile(geo_code, geo_level, session):
    db_model = get_model_from_fields(['highest educational level'], geo_level,
                                     'highesteducationallevel_%s_25andover'
                                     % geo_level)
    objects = get_objects_by_geo(db_model, geo_code, geo_level, session)

    edu_dist_data = {}
    get_or_higher = 0.0
    fet_or_higher = 0.0
    total = 0.0
    for i, obj in enumerate(objects):
        category_val = getattr(obj, 'highest educational level')
        # increment counters
        total += obj.total
        if category_val in EDUCATION_GET_OR_HIGHER:
            get_or_higher += obj.total
            if category_val in EDUCATION_FET_OR_HIGHER:
                fet_or_higher += obj.total
        # add data points for category
        edu_dist_data[str(i)] = {
            "name": category_val,
            "numerators": {"this": obj.total},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        }
    edu_dist_data = collapse_categories(edu_dist_data,
                                        COLLAPSED_EDUCATION_CATEGORIES,
                                        key_order=('None', 'Other',
                                                   '<= Gr 3', 'GET',
                                                   'FET', 'HET',
                                                   'Post-grad'))
    edu_split_data = {
        'percent_get_or_higher': {
            "name": "Completed GET or higher",
            "numerators": {"this": get_or_higher},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        },
        'percent_fet_or_higher': {
            "name": "Completed FET or higher",
            "numerators": {"this": fet_or_higher},
            "error": {"this": 0.0},
            "numerator_errors": {"this": 0.0},
        }
    }
    # calculate percentages
    for data in (edu_dist_data, edu_split_data):
        for fields in data.values():
            fields["values"] = {"this": round(fields["numerators"]["this"]
                                              / total * 100, 2)}

    edu_dist_data['metadata'] = {'universe': 'Invididuals 25 and over'}
    edu_split_data['metadata'] = {'universe': 'Invididuals 25 and over'}

    return {'educational_attainment_distribution': edu_dist_data,
            'educational_attainment': edu_split_data}


def collapse_categories(data, categories, key_order=None):
    if key_order:
        collapsed = OrderedDict((key, {'name': key}) for key in key_order)
    else:
        collapsed = {}

    # level 1: iterate over categories in data
    for fields in data.values():
        new_category_name = categories[fields['name']]
        collapsed.setdefault(new_category_name, {'name': new_category_name})
        new_fields = collapsed[new_category_name]
        # level 2: iterate over measurement objects in category
        for measurement_key, measurement_objects in fields.iteritems():
            if measurement_key == 'name':
                continue
            new_fields.setdefault(measurement_key, {})
            new_measurement_objects = new_fields[measurement_key]
            # level 3: iterate over data points in measurement objects
            for datapoint_key, datapoint_value in measurement_objects.iteritems():
                try:
                    new_measurement_objects.setdefault(datapoint_key, 0)
                    new_measurement_objects[datapoint_key] += float(datapoint_value)
                except (ValueError, TypeError):
                    new_measurement_objects[datapoint_key] = datapoint_value

    return collapsed


def get_objects_by_geo(db_model, geo_code, geo_level, session, order_by=None):
    geo_attr = '%s_code' % geo_level
    objects = session.query(db_model).filter(getattr(db_model, geo_attr)
                                             == geo_code)
    if order_by is not None:
        objects = objects.order_by(getattr(db_model, order_by))
    objects = objects.all()
    if len(objects) == 0:
        raise LocationNotFound("%s.%s with code '%s' not found"
                               % (db_model.__tablename__, geo_attr, geo_code))
    return objects


def calculate_median(objects, field_name):
    '''
    Calculates the median where obj.total is the distribution count and
    getattr(obj, field_name) is the distribution segment.
    Note: this function assumes the objects are sorted.
    '''
    total = 0
    for obj in objects:
        total += obj.total
    half = total / 2.0

    counter = 0
    for i, obj in enumerate(objects):
        counter += obj.total
        if counter > half:
            if counter - half == 1:
                # total must be even (otherwise counter - half ends with .5)
                return (float(getattr(objects[i - 1], field_name)) +
                        float(getattr(obj, field_name))) / 2.0
            return float(getattr(obj, field_name))
        elif counter == half:
            # total must be even (otherwise half ends with .5)
            return (float(getattr(obj, field_name)) +
                    float(getattr(objects[i + 1], field_name))) / 2.0
