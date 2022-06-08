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


def getStats(people, one_gene, two_genes, have_trait):
    stats = {}
    for person in people:
        if person in one_gene:
            if person in have_trait:
                stats[person] = {'gene': 1, 'trait': True, 'prob': 0}
            else:
                stats[person] = {'gene': 1, 'trait': False, 'prob': 0}
        elif person in two_genes:
            if person in have_trait:
                stats[person] = {'gene': 2, 'trait': True, 'prob': 0}
            else:
                stats[person] = {'gene': 2, 'trait': False, 'prob': 0}
        else:
            if person in have_trait:
                stats[person] = {'gene': 0, 'trait': True, 'prob': 0}
            else:
                stats[person] = {'gene': 0, 'trait': False, 'prob': 0}

    return stats


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
    stats = getStats(people, one_gene, two_genes, have_trait)
    for person in people:
        mother = people[person]['mother']
        father = people[person]['father']

        if mother == None:
            gene = stats[person]['gene']
            trait = stats[person]['trait']
            stats[person]['prob'] = round((PROBS["gene"][gene] * PROBS["trait"][gene][trait]), 4)
        else:
            mGenes = stats[mother]['gene']
            fGenes = stats[father]['gene']
            mTraitProb = 0.01
            fTraitProb = 0.01
            if mGenes == 1:
                mTraitProb = 0.50
            elif mGenes == 2:
                mTraitProb = 0.99
            if fGenes == 1:
                fTraitProb = 0.50
            elif fGenes == 2:
                fTraitProb = 0.99

            pGene = stats[person]['gene']
            trait = stats[person]['trait']
            if pGene == 0:
                prob = round(((1 - mTraitProb) * (1 - fTraitProb)), 6)
            elif pGene == 1:
                prob = round((mTraitProb * (1 - fTraitProb)) + (fTraitProb * (1 - mTraitProb)), 6)
            else:
                prob = round((mTraitProb * fTraitProb), 6)

            stats[person]['prob'] = round((prob * PROBS["trait"][pGene][trait]), 6)
            
    finalProb = 1
    for i in stats:
        finalProb *= stats[i]['prob']
    
    return round(finalProb, 8)


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    stats = getStats(probabilities, one_gene, two_genes, have_trait)

    for person in probabilities:
        gene = stats[person]['gene']
        trait = stats[person]['trait']
        probabilities[person]['gene'][gene] += p
        probabilities[person]['trait'][trait] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        gTotal = probabilities[person]['gene'][0] + probabilities[person]['gene'][1] + probabilities[person]['gene'][2]
        tTotal = probabilities[person]['trait'][True] + probabilities[person]['trait'][False]

        probabilities[person]['gene'][0] = round(probabilities[person]['gene'][0] / gTotal, 4)
        probabilities[person]['gene'][1] = round(probabilities[person]['gene'][1] / gTotal, 4)
        probabilities[person]['gene'][2] = round(probabilities[person]['gene'][2] / gTotal, 4)
        probabilities[person]['trait'][True] = round(probabilities[person]['trait'][True] / tTotal, 4)
        probabilities[person]['trait'][False] = round(probabilities[person]['trait'][False] / tTotal, 4)


if __name__ == "__main__":
    main()
