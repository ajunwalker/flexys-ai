classifier_config = {
    'Support Vector Machine': [
        {
            'name'  : 'alpha',
            'type'  : 'continuous',
            'domain': (1e-6, 1e-2),
        },
        {
            'name'  : 'max_iter',
            'type'  : 'discrete',
            'domain': (200,),
        }
    ],
    'Random Forest': [
        {
            'name'  : 'max_depth',
            'type'  : 'discrete',
            'domain': (10, 30, 50),
        },
        {
            'name'  : 'min_samples_split',
            'type'  : 'discrete',
            'domain': (2, 8, 32),
        },
        {
            'name'  : 'n_estimators',
            'type'  : 'discrete',
            'domain': (100, 300),
        }
    ],

}

regressor_config = {
    'Support Vector Machine': [
        {
            'name'  : 'alpha',
            'type'  : 'continuous',
            'domain': (1e-6, 1e-2),
        },
        {
            'name'  : 'max_iter',
            'type'  : 'discrete',
            'domain': (200,),
        }
    ],
    'Random Forest': [
        {
            'name'  : 'max_depth',
            'type'  : 'discrete',
            'domain': (10, 30, 50),
        },
        {
            'name'  : 'min_samples_split',
            'type'  : 'discrete',
            'domain': (2, 8, 32),
        },
        {
            'name'  : 'n_estimators',
            'type'  : 'discrete',
            'domain': (100, 300),
        }
    ],
}

param_types = {
    'alpha': float,
    'max_depth': int,
    'min_samples_split': int,
    'n_estimators': int,
    'max_iter': int,
    'n_neighbors': int
}
