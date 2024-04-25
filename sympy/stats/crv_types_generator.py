def create_method(name, expression, test_cases):
    tests = "\n        ".join([
        f">>> {name}(*{case['params']})\n{case['expected']}"
        for case in test_cases
    ])
    return f"""
    @staticmethod
    def {name}(x, *params):
        '''
        {expression['doc']}

        Examples
        --------
        {tests}
        '''
        if not ({expression['condition']}):
            raise ValueError("Parameter constraints not satisfied for {name}")
        return {expression['formula']}
    """


def generate_distribution_code(distributions, test_cases):
    for name, props in distributions.items():
        param_constraints = " and ".join([f"{key} > 0" for key in props.get('parameter_constraints', {}).keys()])
        methods = []
        for method_name in ['pdf', 'cdf', 'mean', 'variance']:  # Add more functions as needed
            if method_name + '_expression' in props:
                method_info = {
                    'condition': param_constraints,
                    'formula': props[method_name + '_expression'],
                    'doc': f"{method_name} for the {name} distribution"
                }
                methods.append(create_method(method_name, method_info, test_cases[name].get(method_name, [])))

        class_definition = f'''
class {name}(ContinuousRV):
    """{props.get('docstring', 'No documentation available')}
    """
    _argnames = {props['arg_names']}

    {"".join(methods)}
    # Additional statistical methods can be added here
'''
        print(class_definition)

# Example dictionary including Beta and Gamma distributions with new features
distributions = {
    "Beta": {
        "arg_names": "['alpha', 'beta']",
        "pdf_expression": "(x**(alpha-1) * (1-x)**(beta-1)) / gamma(alpha+beta) / (gamma(alpha) * gamma(beta))",
        "cdf_expression": "betainc(alpha, beta, x)",
        "parameter_constraints": {"alpha": "alpha > 0", "beta": "beta > 0"},
        "docstring": "Beta distribution, useful for modeling events with a bounded range, parameters are shape parameters alpha and beta."
    },
    "Gamma": {
        "arg_names": "['k', 'theta']",
        "pdf_expression": "x**(k-1) * exp(-x/theta) / (gamma(k) * theta**k)",
        "cdf_expression": "lowergamma(k, x/theta) / gamma(k)",
        "parameter_constraints": {"k": "k > 0", "theta": "theta > 0"},
        "docstring": "Gamma distribution, commonly used to model waiting times and is characterized by shape parameter k and scale parameter theta."
    }
}

test_cases = {
    "Beta": {
        "pdf": [
            {"params": "(0.5, 0.5, 0.5)", "expected": "1.0"},
            {"params": "(0.5, 0.5, 0)", "expected": "0.0"}
        ],
        "cdf": [
            {"params": "(0.5, 0.5, 0.5)", "expected": "0.5"},
            {"params": "(0.5, 0.5, 1)", "expected": "1.0"}
        ]
    },
    "Gamma": {
        "pdf": [
            {"params": "(1, 1, 1)", "expected": "0.367879"}
        ],
        "cdf": [
            {"params": "(1, 1, 1)", "expected": "0.632120"}
        ]
    }
}

# Generate the code with enhanced features
generate_distribution_code(distributions, test_cases)
