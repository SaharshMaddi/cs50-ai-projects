import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    joint = 1

    for p in people:
        if p in two_genes:
            count = 2
        elif p in one_gene:
            count = 1
        else:
            count = 0

        trait = p in have_trait
        mother = people[p]["mother"]
        father = people[p]["father"]

        if mother is None:
            gene_prob = PROBS["gene"][count]
        else:
            parent_passing = {}
            for parent in [mother, father]:
                if parent in two_genes:
                    parent_passing[parent] = 1 - PROBS["mutation"]
                elif parent in one_gene:
                    parent_passing[parent] = 0.5
                else:
                    # Has 0 genes: passes 1 only if it mutates
                    parent_passing[parent] = PROBS["mutation"]

            p_mom = parent_passing[mother]
            p_dad = parent_passing[father]
            if count == 2:
                gene_prob = p_mom * p_dad
            elif count == 1:
                gene_prob = (p_mom * (1 - p_dad)) + (p_dad * (1 - p_mom))
            else:
                gene_prob = (1 - p_mom) * (1 - p_dad)
        trait_prob = PROBS["trait"][count][trait]
        joint *= (gene_prob * trait_prob)

    return joint

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in two_genes:
            count = 2
        elif person in one_gene:
            count = 1
        else:
            count = 0
        probabilities[person]["gene"][count] +=p

        trait = person in have_trait
        probabilities[person]["trait"][trait]+=p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    # sum must be 1 multiply by constant
    for person in probabilities:
        gene_dict = probabilities[person]["gene"]
        trait_dict = probabilities[person]["trait"]

        gene_sum = sum(gene_dict.values())
        trait_sum = sum(trait_dict.values())

        if gene_sum > 0:
            for count in gene_dict:
                gene_dict[count] /= gene_sum
        if trait_sum > 0:
            for status in trait_dict:
                trait_dict[status] /= trait_sum

if __name__ == "__main__":
    main()
