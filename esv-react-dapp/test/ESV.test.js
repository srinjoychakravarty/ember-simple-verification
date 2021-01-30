require("chai").use(require("chai-as-promised")).should();

const ESV = artifacts.require("./ESV");

contract("ESV", (accounts) => {
  let esv;
  const contract_deployer = accounts[0];
  const original_admin_array = [accounts[0]];

  beforeEach(async () => {
    esv = await ESV.new();
  });

  describe("calibrate initial state", () => {
    it("returns legitimate contract owner", async () => {
      // Retrieve Contract Object deployed to Ganache
      const contract_owner = await esv.getContractOwner(); // Read the Contract Owner
      contract_owner.should.equal(contract_deployer); // Check Contract Owner matches Deployer Ethereum Address
    });

    it("returns contract owner as original administrator", async () => {
      const admins = await esv.getAllAdmins();
      admins.should.to.eql(original_admin_array);
    });

    it("ensures no ethereum addresses are initially stored in state", async () => {
      const eth_addr_count = await esv.getEthereumAddressCount();
      eth_addr_count.toString().should.equal("0");
    });

    it("ensures no message hashes are initially stored in state", async () => {
      const msg_hash_count = await esv.getMessageHashCount();
      msg_hash_count.toString().should.equal("0");
    });

    it("ensures no digital signatures are initially stored in state", async () => {
      const digi_sig_count = await esv.getSignatureCount();
      digi_sig_count.toString().should.equal("0");
    });

    it("ensures no esv items initially stored in state", async () => {
      const esv_item_array = await esv.getAllESVItemIDs();
      expect(esv_item_array).to.be.an("array").that.is.empty;
    });

    it("ensures esv item count starts from null", async () => {
      const esv_item_count = await esv.getESVItemCount();
      esv_item_count.toString().should.equal("0");
    });
  });

  describe("validate esv item crud operations", () => {
    beforeEach(async () => {
      await esv.setESVItemCreate(904, { from: contract_deployer });
    });

    it("confirms created esv item persists in state", async () => {
      const esv_item_array = await esv.getAllESVItemIDs();
      const first_esv_item_bignum = await esv_item_array[0];
      first_esv_item_bignum.toString().should.equal("904");
    });

    it("confirms esv item creation increments count", async () => {
      const esv_count = await esv.getESVItemCount();
      esv_count.toString().should.equal("1");
    });

    it("returns expected keys within esv item", async () => {
      const esv_item_dict = await esv.getESVItem(904);
      expect(esv_item_dict)
        .to.be.an("object")
        .that.has.all.keys("0", "1", "2", "3", "4");
    });

    it('returns "exists" == false for esv item uuid not created', async () => {
      const esv_item_dict = await esv.getESVItem(905);
      const item_exists = await esv_item_dict["0"];
      item_exists.should.equal(false);
    });

    it('returns "exists" == true for created esv item uuid', async () => {
      const esv_item_dict = await esv.getESVItem(904);
      const item_exists = await esv_item_dict["0"];
      item_exists.should.equal(true);
    });
  });
});
